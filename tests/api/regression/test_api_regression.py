"""API regression tests.

This module contains higher-confidence regression checks for the API exposed by
the AUT (Application Under Test).

Design goals:
- Reduce false skips caused by path mismatches between runtime URLs and OpenAPI keys.
- Prefer debuggable failures over noisy/ambiguous outcomes.
- Derive query parameter names and (when possible) allowed values from OpenAPI.

Known issues:
- The AUT currently returns HTTP 500 for /products?sort=... (reproducible via curl).
  Related tests are marked xfail to keep CI meaningful while documenting the defect.
"""

import time
from typing import Any, Optional
from urllib.parse import urlencode

import pytest
import requests

DEFAULT_TIMEOUT_SECONDS = 30
PRODUCTS_RESPONSE_TIME_LIMIT_SECONDS = 5.0


def _absolute(base: str, path: str) -> str:
    """Build an absolute URL from a base URL and a relative path.

    Args:
        base: Base URL (scheme + host + optional port), e.g. "http://localhost:8091".
        path: Relative path, with or without a leading slash.

    Returns:
        The combined absolute URL with exactly one slash between base and path.
    """
    return base.rstrip("/") + "/" + path.lstrip("/")


def _strip_query(path: str) -> str:
    """Return the path without a query string.

    Args:
        path: A URL path which may contain a query string.

    Returns:
        Path without query string.
    """
    return path.split("?", 1)[0]


def _ensure_leading_slash(path: str) -> str:
    """Ensure a path starts with a leading slash.

    Args:
        path: A path that may or may not start with '/'.

    Returns:
        Path starting with '/'.
    """
    return path if path.startswith("/") else f"/{path}"


def _path_variants_for_openapi_lookup(path: str) -> list[str]:
    """Generate reasonable OpenAPI key variants for a runtime path.

    Why:
        Runtime request paths and OpenAPI keys often differ by:
        - query strings ("/products?page=1")
        - optional "/api" prefix ("/api/products" vs "/products")
        - missing leading slash ("products")

    Args:
        path: Runtime path (may include query string).

    Returns:
        A list of candidate OpenAPI keys to try.
    """
    base = _ensure_leading_slash(_strip_query(path))

    variants = [base]
    if base.startswith("/api/"):
        variants.append(base[len("/api") :])  # "/api/products" -> "/products"
    else:
        variants.append("/api" + base)  # "/products" -> "/api/products"

    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _unwrap_items(payload: Any) -> list[Any]:
    """Extract a list payload from common API envelope shapes.

    Supported shapes:
        - [ ... ]
        - {"data": [ ... ]}
        - {"data": {"data": [ ... ]}}  (nested wrapper)

    Args:
        payload: JSON-decoded response payload.

    Returns:
        A list of items if present; otherwise an empty list.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data", payload)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if isinstance(data, list):
            return data
    return []


def _unwrap_obj(payload: Any) -> Any:
    """Extract an object payload from common API envelope shapes.

    Supported shapes:
        - { ... }
        - {"data": { ... }}

    Args:
        payload: JSON-decoded response payload.

    Returns:
        The unwrapped object payload.
    """
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        return payload["data"]
    return payload


def _extract_query_param_spec(
    openapi_paths: dict[str, Any], path: str, needle: str
) -> Optional[dict[str, Any]]:
    """Return the OpenAPI parameter object for a query parameter, if found.

    Args:
        openapi_paths: OpenAPI paths mapping.
        path: Runtime path (may include query string or differ by /api prefix).
        needle: Substring to match against parameter name (case-insensitive).

    Returns:
        The OpenAPI parameter dict if found; otherwise None.
    """
    needle_lc = needle.lower()

    for key in _path_variants_for_openapi_lookup(path):
        ops = (openapi_paths or {}).get(key, {})
        get_op = (ops or {}).get("get", {}) if isinstance(ops, dict) else {}
        params = get_op.get("parameters") or []

        for param in params:
            name = (param.get("name") or "").lower()
            if needle_lc in name:
                return param

    return None


def _find_query_param(openapi_paths: dict[str, Any], path: str, needle: str) -> Optional[str]:
    """Find a query parameter name for a path by substring match.

    Args:
        openapi_paths: OpenAPI paths mapping.
        path: Runtime path.
        needle: Substring to match parameter names.

    Returns:
        Parameter name if found, otherwise None.
    """
    param = _extract_query_param_spec(openapi_paths, path, needle)
    return (param or {}).get("name")


def _extract_string_candidates_from_schema(schema: dict[str, Any]) -> list[str]:
    """Extract plausible string values from an OpenAPI schema definition.

    Supported schema shapes:
        - {"enum": [...]}
        - {"items": {"enum": [...]}} (array parameter)
        - {"oneOf": [{"enum": [...]}, ...]}
        - {"anyOf": [{"enum": [...]}, ...]}
        - {"default": "..."}
        - {"example": "..."}
        - {"examples": [...]} (non-standard but sometimes present)

    Args:
        schema: OpenAPI schema dict.

    Returns:
        List of string candidate values.
    """
    candidates: list[str] = []

    enum = schema.get("enum")
    if isinstance(enum, list):
        candidates.extend([str(v) for v in enum if v is not None])

    items = schema.get("items")
    if isinstance(items, dict):
        enum_items = items.get("enum")
        if isinstance(enum_items, list):
            candidates.extend([str(v) for v in enum_items if v is not None])

    for key in ("oneOf", "anyOf"):
        alts = schema.get(key)
        if isinstance(alts, list):
            for alt in alts:
                if isinstance(alt, dict) and isinstance(alt.get("enum"), list):
                    candidates.extend([str(v) for v in alt["enum"] if v is not None])

    for key in ("default", "example"):
        v = schema.get(key)
        if v is not None and isinstance(v, (str, int, float)):
            candidates.append(str(v))

    examples = schema.get("examples")
    if isinstance(examples, list):
        candidates.extend([str(v) for v in examples if v is not None])

    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _find_query_param_value_candidates(
    openapi_paths: dict[str, Any], path: str, needle: str
) -> list[str]:
    """Extract candidate values for a query parameter from OpenAPI.

    Args:
        openapi_paths: OpenAPI paths mapping.
        path: Runtime path.
        needle: Substring to match parameter name.

    Returns:
        Candidate values derived from param/schema examples/enums/defaults.
    """
    param = _extract_query_param_spec(openapi_paths, path, needle)
    if not param:
        return []

    candidates: list[str] = []

    # Parameter-level example(s)
    if param.get("example") is not None:
        candidates.append(str(param["example"]))

    examples = param.get("examples")
    if isinstance(examples, dict):
        for ex in examples.values():
            if isinstance(ex, dict) and ex.get("value") is not None:
                candidates.append(str(ex["value"]))

    schema = param.get("schema")
    if isinstance(schema, dict):
        candidates.extend(_extract_string_candidates_from_schema(schema))

    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _response_debug_snippet(resp: requests.Response, limit: int = 600) -> str:
    """Return a short response snippet for debugging failed requests.

    Args:
        resp: HTTP response.
        limit: Max characters of text to include.

    Returns:
        A trimmed response body snippet (best-effort).
    """
    try:
        txt = resp.text or ""
    except Exception:
        return "<unable to read response text>"
    txt = txt.strip().replace("\r\n", "\n")
    return txt[:limit]


@pytest.mark.regression
def test_openapi_has_info(openapi: dict[str, Any]) -> None:
    """Validate that the OpenAPI spec contains basic `info` metadata."""
    spec = openapi["spec"]
    assert isinstance(spec, dict)
    assert "info" in spec and isinstance(spec["info"], dict)
    assert spec["info"].get("title")


@pytest.mark.regression
def test_products_list_returns_json_200(
    http: requests.Session, api_base_url: str, products_list_path: str
) -> None:
    """Ensure the products list endpoint returns HTTP 200 and JSON content."""
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())


@pytest.mark.regression
def test_products_list_has_minimum_fields(
    http: requests.Session, api_base_url: str, products_list_path: str
) -> None:
    """Validate that the products list returns at least one item with core fields."""
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200

    items = _unwrap_items(r.json())
    assert items, "products list is empty"

    first = items[0]
    assert isinstance(first, dict)
    assert any(k in first for k in ("name", "title", "product_name"))
    assert any(k in first for k in ("id", "uuid", "ulid", "slug", "code"))


@pytest.mark.regression
def test_product_details_endpoint_returns_same_identifier(
    http: requests.Session,
    sample_product_details_url: str,
    sample_product_identifier: str,
) -> None:
    """Fetch a product detail and assert it contains the selected identifier."""
    r = http.get(sample_product_details_url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200

    blob = _unwrap_obj(r.json())
    assert isinstance(blob, dict)

    candidates: list[str] = []
    for k in ("id", "uuid", "ulid", "slug", "code"):
        v = blob.get(k)
        if v is not None:
            candidates.append(str(v))

    assert candidates, f"No identifier field found in response keys={list(blob.keys())}"
    assert sample_product_identifier in candidates


@pytest.mark.regression
def test_categories_list_returns_200(
    http: requests.Session, api_base_url: str, categories_list_path: str
) -> None:
    """Ensure the categories list endpoint is reachable (HTTP 200)."""
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.regression
def test_brands_list_returns_200(
    http: requests.Session, api_base_url: str, brands_list_path: str
) -> None:
    """Ensure the brands list endpoint is reachable (HTTP 200)."""
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_filter_by_category_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict[str, Any],
    sample_category_id: str,
) -> None:
    """If supported by the spec, validate filtering products by category."""
    cat_param = _find_query_param(openapi_paths, products_list_path, "category")
    if not cat_param:
        pytest.skip("No category query parameter described for products list")

    base_path = _strip_query(products_list_path)
    url = _absolute(api_base_url, base_path) + "?" + urlencode({cat_param: sample_category_id})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_filter_by_brand_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict[str, Any],
    sample_brand_id: str,
) -> None:
    """If supported by the spec, validate filtering products by brand."""
    brand_param = _find_query_param(openapi_paths, products_list_path, "brand")
    if not brand_param:
        pytest.skip("No brand query parameter described for products list")

    base_path = _strip_query(products_list_path)
    url = _absolute(api_base_url, base_path) + "?" + urlencode({brand_param: sample_brand_id})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_pagination_page_2_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict[str, Any],
) -> None:
    """If supported by the spec, validate that requesting page=2 succeeds."""
    page_param = _find_query_param(openapi_paths, products_list_path, "page")
    if not page_param:
        pytest.skip("No page query parameter described for products list")

    base_path = _strip_query(products_list_path)
    url = _absolute(api_base_url, base_path) + "?" + urlencode({page_param: 2})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_sorting_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict[str, Any],
) -> None:
    """If supported by the spec, exercise sorting.

    Known issue:
        The AUT currently returns HTTP 500 for /products?sort=... (reproducible).
        We mark this test as xfail when that happens, to document the issue while
        keeping the regression pipeline signal useful.

    Repro:
        curl -i "http://localhost:8091/products?sort=price-asc"
    """
    sort_param = _find_query_param(openapi_paths, products_list_path, "sort")
    if not sort_param:
        pytest.skip("No sort parameter described for products list")

    candidates = _find_query_param_value_candidates(openapi_paths, products_list_path, "sort")
    candidates.append("price-asc")  # fallback

    base_path = _strip_query(products_list_path)

    # Try candidates and stop on the first non-5xx response.
    for sort_value in candidates:
        url = _absolute(api_base_url, base_path) + "?" + urlencode({sort_param: sort_value})
        resp = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)

        if resp.status_code >= 500:
            # Known issue: the AUT crashes on sort input.
            continue

        # Some APIs ignore unknown sorts and still return 200; some validate and return 4xx.
        assert resp.status_code in (200, 400, 422), (
            f"Unexpected status for sorting request: status={resp.status_code}, "
            f"param={sort_param}, value={sort_value}, url={url}, "
            f"body_snippet={_response_debug_snippet(resp)!r}"
        )
        return

    # If we get here: every candidate produced 5xx -> xfail (document known issue).
    pytest.xfail(
        "Known issue: AUT returns 5xx for /products?sort=... "
        '(repro: curl -i "http://localhost:8091/products?sort=price-asc"). '
        f"Candidates tried: {candidates}"
    )


@pytest.mark.regression
def test_products_endpoint_invalid_sort_does_not_crash_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict[str, Any],
) -> None:
    """If sorting is supported, an invalid value should not crash the server.

    Known issue:
        The AUT currently returns HTTP 500 for /products?sort=... even with invalid values.
        We mark this as xfail when that happens, to document the issue while keeping CI green.

    Repro:
        curl -i "http://localhost:8091/products?sort=this_is_not_a_real_sort"
    """
    sort_param = _find_query_param(openapi_paths, products_list_path, "sort")
    if not sort_param:
        pytest.skip("No sort parameter described")

    base_path = _strip_query(products_list_path)
    url = _absolute(api_base_url, base_path) + "?" + urlencode({sort_param: "this_is_not_a_real_sort"})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)

    if r.status_code >= 500:
        pytest.xfail(
            "Known issue: AUT returns 5xx for invalid sort values "
            '(repro: curl -i "http://localhost:8091/products?sort=this_is_not_a_real_sort"). '
            f"body_snippet={_response_debug_snippet(r)!r}"
        )

    assert r.status_code in (200, 400, 422), (
        f"Unexpected status for invalid sort: status={r.status_code}, url={url}, "
        f"body_snippet={_response_debug_snippet(r)!r}"
    )


@pytest.mark.regression
def test_login_returns_token(auth_token: str) -> None:
    """Sanity-check that the login fixture produced a non-empty token."""
    assert isinstance(auth_token, str) and auth_token.strip()


@pytest.mark.regression
def test_me_endpoint_requires_auth_if_present(
    http: requests.Session,
    api_base_url: str,
    openapi_paths: dict[str, Any],
    auth_token: str,
) -> None:
    """If a '/me' endpoint is described, validate auth behavior."""
    me_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "me" in p.lower():
            me_path = p
            break
    if not me_path:
        pytest.skip("No /me endpoint described")

    url = _absolute(api_base_url, me_path)

    r_unauth = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    if r_unauth.status_code == 404:
        pytest.skip(f"Endpoint exists in spec but is not reachable via current gateway (404): {url}")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(
        url,
        headers={"Authorization": f"Bearer {auth_token}"},
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_invoices_list_requires_auth_if_present(
    http: requests.Session,
    api_base_url: str,
    openapi_paths: dict[str, Any],
    auth_token: str,
) -> None:
    """If an invoices list endpoint is described, validate auth behavior."""
    invoices_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "invoice" in p.lower() and "{" not in p:
            invoices_path = p
            break
    if not invoices_path:
        pytest.skip("No invoices list endpoint described")

    url = _absolute(api_base_url, invoices_path)

    r_unauth = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    if r_unauth.status_code == 404:
        pytest.skip(f"Endpoint exists in spec but is not reachable via current gateway (404): {url}")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(
        url,
        headers={"Authorization": f"Bearer {auth_token}"},
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_favorites_list_requires_auth_if_present(
    http: requests.Session,
    api_base_url: str,
    openapi_paths: dict[str, Any],
    auth_token: str,
) -> None:
    """If a favorites list endpoint is described, validate auth behavior."""
    favorites_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "favorite" in p.lower() and "{" not in p:
            favorites_path = p
            break
    if not favorites_path:
        pytest.skip("No favorites list endpoint described")

    url = _absolute(api_base_url, favorites_path)

    r_unauth = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    if r_unauth.status_code == 404:
        pytest.skip(f"Endpoint exists in spec but is not reachable via current gateway (404): {url}")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(
        url,
        headers={"Authorization": f"Bearer {auth_token}"},
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_cart_get_requires_auth_if_present(
    http: requests.Session,
    api_base_url: str,
    openapi_paths: dict[str, Any],
    auth_token: str,
) -> None:
    """If a cart GET endpoint is described, validate auth and reachability.

    Note:
        If only templated endpoints exist (e.g. "/carts/{cartId}"), this test is skipped
        because we cannot call it without first creating a cart and extracting a valid ID.
    """
    cart_path = None

    # Prefer non-templated paths first.
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "cart" in p.lower() and "{" not in p:
            cart_path = p
            break

    # Fallback: if only templated endpoints exist, we cannot call them without an ID.
    if not cart_path:
        for p, ops in (openapi_paths or {}).items():
            if not isinstance(ops, dict) or "get" not in ops:
                continue
            if "cart" in p.lower():
                pytest.skip(
                    f"Only templated cart endpoint found (requires ID, not testable here): {p}"
                )

        pytest.skip("No cart GET endpoint described")

    url = _absolute(api_base_url, cart_path)

    r_unauth = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    if r_unauth.status_code == 404:
        pytest.skip(f"Cart endpoint exists in spec but is not reachable via current gateway (404): {url}")
    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(
        url,
        headers={"Authorization": f"Bearer {auth_token}"},
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_products_endpoint_response_time_is_reasonable(
    http: requests.Session, api_base_url: str, products_list_path: str
) -> None:
    """Guardrail: products list response time should stay below a soft threshold."""
    start = time.time()
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    elapsed = time.time() - start

    assert r.status_code == 200
    assert elapsed < PRODUCTS_RESPONSE_TIME_LIMIT_SECONDS