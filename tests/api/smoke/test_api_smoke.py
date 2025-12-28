"""API smoke tests.

These tests validate the most critical API surfaces to quickly detect whether the
system is up and responding correctly.

Principles:
- Keep smoke tests fast and high-signal.
- Use defensive parsing for list payloads that may be wrapped in envelope objects.
- If a capability is described by OpenAPI but cannot be verified safely (missing
  parameter or missing identifier in sample data), skip instead of producing
  noisy failures.
"""

from typing import Any, Optional
from urllib.parse import urlencode

import pytest
import requests

DEFAULT_TIMEOUT_SECONDS = 30


def _absolute(base: str, path: str) -> str:
    """Join a base URL and a path with exactly one slash.

    Args:
        base: Base URL, e.g. "http://localhost:8091".
        path: Relative path, e.g. "/products" or "products".

    Returns:
        Combined absolute URL.
    """
    return base.rstrip("/") + "/" + path.lstrip("/")


def _unwrap_list_payload(data: Any) -> Optional[list[Any]]:
    """Normalize list responses that may be wrapped in a `data` envelope.

    Supported shapes:
        - [ ... ]
        - {"data": [ ... ]}
        - {"data": {"data": [ ... ]}}

    Args:
        data: JSON-decoded response payload.

    Returns:
        The extracted list if present; otherwise None.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "data" in data:
        inner = data["data"]
        if isinstance(inner, list):
            return inner
        if isinstance(inner, dict) and "data" in inner and isinstance(inner["data"], list):
            return inner["data"]

    return None


def _find_list_path(openapi_paths: dict, keyword: str) -> str | None:
    """Find a GET collection endpoint in OpenAPI paths.

    Note:
        This helper is not currently used by the tests in this module but is kept
        as a utility for future smoke coverage expansion.

    Args:
        openapi_paths: OpenAPI `paths` mapping (path -> operations).
        keyword: Substring to locate the collection endpoint (case-insensitive).

    Returns:
        The matching path if found (non-templated), otherwise None.
    """
    kw = keyword.lower()
    for p, ops in openapi_paths.items():
        if kw in p.lower() and "{" not in p and isinstance(ops, dict) and "get" in ops:
            return p
    return None


@pytest.mark.smoke
def test_swagger_ui_is_reachable(http: requests.Session, api_docs_url: str) -> None:
    """Verify the Swagger UI page is reachable and looks like HTML.

    Args:
        http: Shared requests session fixture.
        api_docs_url: Swagger UI URL, derived in conftest.py.
    """
    r = http.get(api_docs_url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200
    # Swagger UI is HTML.
    assert "<title" in r.text.lower()


@pytest.mark.smoke
def test_openapi_spec_is_loadable(openapi_spec: dict) -> None:
    """Verify the OpenAPI JSON spec can be loaded and contains paths.

    Args:
        openapi_spec: Parsed OpenAPI document fixture.
    """
    assert isinstance(openapi_spec, dict)
    assert "paths" in openapi_spec and openapi_spec["paths"]


@pytest.mark.smoke
def test_products_list_returns_200(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
) -> None:
    """Verify the products list endpoint returns 200 and JSON content.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        products_list_path: Products list path derived from OpenAPI (or fallback).
    """
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())


@pytest.mark.smoke
def test_products_list_is_not_empty(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
) -> None:
    """Verify the products list endpoint returns at least one item.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        products_list_path: Products list path derived from OpenAPI (or fallback).
    """
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200

    items = _unwrap_list_payload(r.json())
    assert isinstance(items, list)
    assert len(items) > 0


@pytest.mark.smoke
def test_product_details_for_first_item(
    http: requests.Session,
    sample_product_details_url: str,
) -> None:
    """Verify product details endpoint returns JSON for a valid product.

    Note:
        The URL is resolved robustly in conftest.py by probing identifiers until the API returns 200.

    Args:
        http: Shared requests session fixture.
        sample_product_details_url: Concrete product details URL fixture.
    """
    r = http.get(sample_product_details_url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())
    data = r.json()
    assert isinstance(data, (dict, list))


@pytest.mark.smoke
def test_categories_list_returns_200(
    http: requests.Session,
    api_base_url: str,
    categories_list_path: str,
) -> None:
    """Verify the categories list endpoint is reachable.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        categories_list_path: Categories list path derived from OpenAPI (or fallback).
    """
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.smoke
def test_brands_list_returns_200(
    http: requests.Session,
    api_base_url: str,
    brands_list_path: str,
) -> None:
    """Verify the brands list endpoint is reachable.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        brands_list_path: Brands list path derived from OpenAPI (or fallback).
    """
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.smoke
def test_products_endpoint_supports_pagination_if_described(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
) -> None:
    """If OpenAPI describes pagination, verify requesting page 2 returns 200.

    This test does not assume pagination exists; it discovers a pagination parameter
    from OpenAPI. If none is described, the test is skipped.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        products_list_path: Products list path derived from OpenAPI (or fallback).
        openapi_paths: OpenAPI `paths` mapping.
    """
    ops = openapi_paths.get(products_list_path) or {}
    get_op = ops.get("get") or {}
    params = get_op.get("parameters") or []

    page_param = None
    for p in params:
        name = (p.get("name") or "").lower()
        if name in ("page", "p", "pageindex", "pagenumber"):
            page_param = p.get("name")
            break

    if not page_param:
        pytest.skip("No pagination parameter described for products list endpoint in OpenAPI spec")

    url = _absolute(api_base_url, products_list_path) + "?" + urlencode({page_param: 2})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.smoke
def test_filter_products_by_category_param_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_product: dict,
) -> None:
    """If OpenAPI describes a category filter, verify the filter request returns 200.

    The test:
    - discovers a category-related query parameter from OpenAPI,
    - extracts a category identifier from the sample product,
    - issues a filtered request and expects 200.

    If the parameter is not described or the sample product lacks a category identifier,
    the test is skipped.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        products_list_path: Products list path derived from OpenAPI (or fallback).
        openapi_paths: OpenAPI `paths` mapping.
        sample_product: Sample product object fixture.
    """
    # We try to discover a category filter parameter from OpenAPI.
    ops = openapi_paths.get(products_list_path) or {}
    get_op = ops.get("get") or {}
    params = get_op.get("parameters") or []

    cat_param = None
    for p in params:
        name = (p.get("name") or "").lower()
        if "category" in name:
            cat_param = p.get("name")
            break

    if not cat_param:
        pytest.skip("No category filter parameter described for products list endpoint in OpenAPI spec")

    # Try to pick a category id/name from the sample product if present; otherwise skip.
    candidate = None
    for key in ("category_id", "categoryId", "category", "category_slug", "categorySlug"):
        v = sample_product.get(key)
        if v is not None and str(v).strip():
            candidate = str(v).strip()
            break

    if not candidate:
        pytest.skip(
            "Sample product does not expose a category identifier; cannot test category filter safely"
        )

    url = _absolute(api_base_url, products_list_path) + "?" + urlencode({cat_param: candidate})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200


@pytest.mark.smoke
def test_filter_products_by_brand_param_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_product: dict,
) -> None:
    """If OpenAPI describes a brand filter, verify the filter request returns 200.

    The test:
    - discovers a brand-related query parameter from OpenAPI,
    - extracts a brand identifier from the sample product,
    - issues a filtered request and expects 200.

    If the parameter is not described or the sample product lacks a brand identifier,
    the test is skipped.

    Args:
        http: Shared requests session fixture.
        api_base_url: Base URL determined in conftest.py.
        products_list_path: Products list path derived from OpenAPI (or fallback).
        openapi_paths: OpenAPI `paths` mapping.
        sample_product: Sample product object fixture.
    """
    ops = openapi_paths.get(products_list_path) or {}
    get_op = ops.get("get") or {}
    params = get_op.get("parameters") or []

    brand_param = None
    for p in params:
        name = (p.get("name") or "").lower()
        if "brand" in name:
            brand_param = p.get("name")
            break

    if not brand_param:
        pytest.skip("No brand filter parameter described for products list endpoint in OpenAPI spec")

    candidate = None
    for key in ("brand_id", "brandId", "brand", "brand_slug", "brandSlug"):
        v = sample_product.get(key)
        if v is not None and str(v).strip():
            candidate = str(v).strip()
            break

    if not candidate:
        pytest.skip(
            "Sample product does not expose a brand identifier; cannot test brand filter safely"
        )

    url = _absolute(api_base_url, products_list_path) + "?" + urlencode({brand_param: candidate})
    r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
    assert r.status_code == 200