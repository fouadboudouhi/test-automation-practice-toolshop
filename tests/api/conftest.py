"""Pytest configuration and shared fixtures for API tests.

This file centralizes:
- HTTP session setup
- OpenAPI spec discovery (via Swagger UI HTML)
- Derivation of common endpoint paths from OpenAPI
- Sample data fixtures (product/category/brand)
- Optional auth token fixture (skips if login is not supported or creds are invalid)

Environment variables
---------------------
- API_HOST:
    Base host where nginx exposes the API.
    Default: "http://localhost:8091"

- API_DOCS_URL:
    URL to the Swagger UI HTML page.
    Default: f"{API_HOST}/api/documentation"

- DEMO_EMAIL / DEMO_PASSWORD:
    Demo credentials for login-based tests.
    Defaults:
      DEMO_EMAIL="customer@practicesoftwaretesting.com"
      DEMO_PASSWORD="welcome01"
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

import pytest
import requests

DEFAULT_TIMEOUT_SECONDS = 30
PROBE_TIMEOUT_SECONDS = 15

# Regex used to extract the OpenAPI JSON URL from Swagger UI HTML.
# Example:
#   url: "http://localhost:8091/docs?api-docs.json"
OPENAPI_URL_PATTERN = re.compile(r'url:\s*"([^"]+)"')


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _env(name: str, default: str) -> str:
    """Read an environment variable with a safe default.

    Args:
        name: Environment variable name.
        default: Fallback value if variable is missing or empty.

    Returns:
        The environment variable value (stripped) if present and non-empty,
        otherwise the provided default.
    """
    v = os.getenv(name)
    return v.strip() if isinstance(v, str) and v.strip() else default


def _absolute(base: str, path: str) -> str:
    """Join a base URL and a relative path with exactly one slash.

    Args:
        base: Base URL, e.g. "http://localhost:8091".
        path: Relative path, e.g. "/products" or "products".

    Returns:
        Combined absolute URL.
    """
    return base.rstrip("/") + "/" + path.lstrip("/")


def _unwrap_items(payload: Any) -> list[Any]:
    """Unwrap list responses that may be enveloped in `data`.

    Tolerates common pagination / envelope shapes:
    - [ ... ]
    - { "data": [ ... ] }
    - { "data": { "data": [ ... ] } }

    Args:
        payload: JSON-decoded response payload.

    Returns:
        A list of items or an empty list if no list could be extracted.
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


def _first_identifier(items: list[Any]) -> Optional[str]:
    """Extract the first usable identifier from a list of dict items.

    Args:
        items: List of items (expected to be dicts).

    Returns:
        A string identifier if found; otherwise None.
    """
    for it in items:
        if not isinstance(it, dict):
            continue
        for k in ("id", "uuid", "ulid", "slug", "code"):
            v = it.get(k)
            if isinstance(v, (str, int)) and str(v).strip():
                return str(v).strip()
    return None


def _find_list_path(openapi_paths: dict[str, Any], needle: str) -> Optional[str]:
    """Find a GET collection endpoint like "/products" (non-templated).

    Args:
        openapi_paths: OpenAPI `paths` object (path -> operations).
        needle: Substring to search for (case-insensitive).

    Returns:
        Path string if found; otherwise None.
    """
    needle = needle.lower()
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict):
            continue
        if "get" not in ops:
            continue
        low = p.lower()
        if needle in low and "{" not in p:
            return p
    return None


def _find_details_path(openapi_paths: dict[str, Any], needle: str) -> Optional[str]:
    """Find a GET details endpoint like "/products/{id}" (templated).

    Args:
        openapi_paths: OpenAPI `paths` object (path -> operations).
        needle: Substring to search for (case-insensitive).

    Returns:
        Path string if found; otherwise None.
    """
    needle = needle.lower()
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict):
            continue
        if "get" not in ops:
            continue
        low = p.lower()
        if needle in low and "{" in p:
            return p
    return None


def _replace_first_path_param(path: str, value: str) -> str:
    """Replace the first "{...}" path parameter with a concrete value.

    Args:
        path: Templated path, e.g. "/products/{id}".
        value: Replacement value.

    Returns:
        Path with the first template replaced, e.g. "/products/123".
    """
    return re.sub(r"\{[^}]+\}", value, path, count=1)


# -----------------------------------------------------------------------------
# Core fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def http() -> requests.Session:
    """Create a shared HTTP session for the test session.

    Returns:
        A configured requests.Session with JSON accept header.
    """
    s = requests.Session()
    s.headers.update({"accept": "application/json"})
    return s


@pytest.fixture(scope="session")
def api_host() -> str:
    """Return the externally reachable API host (nginx).

    Returns:
        API host base URL without trailing slash.
    """
    return _env("API_HOST", "http://localhost:8091").rstrip("/")


@pytest.fixture(scope="session")
def api_docs_url(api_host: str) -> str:
    """Return the Swagger UI HTML URL used to discover the OpenAPI JSON URL.

    Args:
        api_host: Base host where nginx exposes the API.

    Returns:
        Swagger UI URL.
    """
    return _env("API_DOCS_URL", f"{api_host}/api/documentation")


@pytest.fixture(scope="session")
def openapi_spec_url(http: requests.Session, api_docs_url: str, api_host: str) -> str:
    """Extract the OpenAPI JSON URL from Swagger UI HTML.

    Args:
        http: Shared HTTP session fixture.
        api_docs_url: Swagger UI HTML page URL.
        api_host: Base host where nginx exposes the API.

    Returns:
        URL to the OpenAPI JSON document.
    """
    r = http.get(api_docs_url, timeout=DEFAULT_TIMEOUT_SECONDS)
    r.raise_for_status()

    m = OPENAPI_URL_PATTERN.search(r.text)
    if m:
        return m.group(1)

    # Fallback (best-effort)
    return f"{api_host}/docs?api-docs.json"


@pytest.fixture(scope="session")
def openapi_spec(http: requests.Session, openapi_spec_url: str) -> dict[str, Any]:
    """Download and validate the OpenAPI spec JSON.

    Args:
        http: Shared HTTP session fixture.
        openapi_spec_url: URL to the OpenAPI JSON document.

    Returns:
        Parsed OpenAPI document as a dict.

    Raises:
        RuntimeError: If the JSON doesn't look like an OpenAPI document.
    """
    r = http.get(openapi_spec_url, timeout=DEFAULT_TIMEOUT_SECONDS)
    r.raise_for_status()

    spec = r.json()
    if not isinstance(spec, dict) or "paths" not in spec:
        raise RuntimeError(
            "OpenAPI spec JSON did not look like an OpenAPI document (missing 'paths')."
        )
    return spec


@pytest.fixture(scope="session")
def openapi_paths(openapi_spec: dict[str, Any]) -> dict[str, Any]:
    """Return OpenAPI `paths` mapping."""
    return openapi_spec.get("paths", {}) or {}


@pytest.fixture(scope="session")
def openapi(openapi_spec: dict[str, Any], openapi_paths: dict[str, Any], openapi_spec_url: str) -> dict[str, Any]:
    """Compatibility fixture for tests expecting `openapi['spec']`.

    Returns:
        Dict with keys: spec, paths, spec_url.
    """
    return {"spec": openapi_spec, "paths": openapi_paths, "spec_url": openapi_spec_url}


# -----------------------------------------------------------------------------
# Path fixtures (derived from OpenAPI with safe fallbacks)
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def products_list_path(openapi_paths: dict[str, Any]) -> str:
    """Return the products collection endpoint path."""
    return _find_list_path(openapi_paths, "products") or "/products"


@pytest.fixture(scope="session")
def categories_list_path(openapi_paths: dict[str, Any]) -> str:
    """Return the categories collection endpoint path."""
    return _find_list_path(openapi_paths, "categories") or "/categories"


@pytest.fixture(scope="session")
def brands_list_path(openapi_paths: dict[str, Any]) -> str:
    """Return the brands collection endpoint path."""
    return _find_list_path(openapi_paths, "brands") or "/brands"


@pytest.fixture(scope="session")
def product_details_path(openapi_paths: dict[str, Any]) -> str:
    """Return the product details endpoint path (templated)."""
    return _find_details_path(openapi_paths, "products") or "/products/{id}"


@pytest.fixture(scope="session")
def api_base_url(http: requests.Session, api_host: str, products_list_path: str) -> str:
    """Auto-detect the API base URL once per session.

    Some stacks expose endpoints at:
      - http://host/products
    others at:
      - http://host/api/products

    The detection probes the products list path against both variants.

    Args:
        http: Shared HTTP session fixture.
        api_host: External host base URL.
        products_list_path: Products collection path.

    Returns:
        The detected base URL (either api_host or api_host + "/api").

    Raises:
        RuntimeError: If both probes fail.
    """
    # Probe style A: host + /products
    url_a = _absolute(api_host, products_list_path)
    try:
        ra = http.get(url_a, timeout=PROBE_TIMEOUT_SECONDS)
        if ra.status_code != 404 and ra.status_code < 500:
            return api_host
    except Exception:
        pass

    # Probe style B: host + /api + /products
    api_prefix = api_host + "/api"
    url_b = _absolute(api_prefix, products_list_path)
    try:
        rb = http.get(url_b, timeout=PROBE_TIMEOUT_SECONDS)
        if rb.status_code != 404 and rb.status_code < 500:
            return api_prefix
    except Exception:
        pass

    raise RuntimeError(
        "Could not determine API base URL. Probes failed:\n"
        f" - {url_a}\n"
        f" - {url_b}\n"
        "Check nginx routing or products_list_path."
    )


# -----------------------------------------------------------------------------
# Sample data fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def sample_product(http: requests.Session, api_base_url: str, products_list_path: str) -> dict[str, Any]:
    """Fetch and return the first product from the products list.

    Args:
        http: Shared HTTP session fixture.
        api_base_url: Detected API base URL.
        products_list_path: Products collection path.

    Returns:
        A product object (dict).

    Skips:
        If the products list is empty or not in the expected shape.
    """
    r = http.get(_absolute(api_base_url, products_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    r.raise_for_status()

    items = _unwrap_items(r.json())
    if not items:
        pytest.skip("Products list is empty; cannot pick sample product.")
    if not isinstance(items[0], dict):
        pytest.skip("First product item is not an object/dict.")
    return items[0]


@pytest.fixture(scope="session")
def sample_product_identifier(
    http: requests.Session,
    api_base_url: str,
    product_details_path: str,
    sample_product: dict[str, Any],
) -> str:
    """Pick a product identifier that actually works against the details endpoint.

    IMPORTANT:
    - We try multiple candidate fields (id/slug/uuid/ulid/code).
    - We validate by calling the details endpoint until we find a candidate that yields HTTP 200.

    Args:
        http: Shared HTTP session fixture.
        api_base_url: Detected API base URL.
        product_details_path: Templated product details path.
        sample_product: Sample product object.

    Returns:
        A working product identifier string.

    Skips:
        If no usable identifier exists or none yields a 200 details response.
    """
    candidates: list[str] = []
    for k in ("id", "slug", "uuid", "ulid", "code"):
        v = sample_product.get(k)
        if isinstance(v, (str, int)) and str(v).strip():
            candidates.append(str(v).strip())

    if not candidates:
        pytest.skip(
            f"Sample product had no usable identifier fields: keys={list(sample_product.keys())}"
        )

    for cand in candidates:
        path = _replace_first_path_param(product_details_path, cand)
        url = _absolute(api_base_url, path)
        try:
            r = http.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
            if r.status_code == 200:
                return cand
        except Exception:
            continue

    pytest.skip(
        "Could not find a working identifier for product details endpoint. "
        f"Tried {candidates} on path {product_details_path}"
    )


@pytest.fixture(scope="session")
def sample_product_details_url(
    api_base_url: str, product_details_path: str, sample_product_identifier: str
) -> str:
    """Return a concrete product details URL for the chosen sample identifier."""
    return _absolute(
        api_base_url,
        _replace_first_path_param(product_details_path, sample_product_identifier),
    )


@pytest.fixture(scope="session")
def sample_product_id(sample_product_identifier: str) -> str:
    """Alias for older tests that still expect sample_product_id."""
    return sample_product_identifier


@pytest.fixture(scope="session")
def sample_category_id(http: requests.Session, api_base_url: str, categories_list_path: str) -> str:
    """Return a sample category identifier derived from the categories list."""
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    r.raise_for_status()

    cid = _first_identifier(_unwrap_items(r.json()))
    if not cid:
        pytest.skip("Could not extract a sample category id.")
    return cid


@pytest.fixture(scope="session")
def sample_brand_id(http: requests.Session, api_base_url: str, brands_list_path: str) -> str:
    """Return a sample brand identifier derived from the brands list."""
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=DEFAULT_TIMEOUT_SECONDS)
    r.raise_for_status()

    bid = _first_identifier(_unwrap_items(r.json()))
    if not bid:
        pytest.skip("Could not extract a sample brand id.")
    return bid


# -----------------------------------------------------------------------------
# Auth fixture
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def auth_token(http: requests.Session, api_base_url: str, openapi_paths: dict[str, Any]) -> str:
    """Try to login and return a bearer token.

    The fixture is intentionally defensive:
    - If no login endpoint is described in OpenAPI, tests that depend on auth are skipped.
    - If credentials are invalid or the response doesn't contain a token, tests are skipped.

    Env:
        DEMO_EMAIL / DEMO_PASSWORD can be overridden for local runs.

    Args:
        http: Shared HTTP session fixture.
        api_base_url: Detected API base URL.
        openapi_paths: OpenAPI paths/operations mapping.

    Returns:
        A token string.

    Skips:
        If login is not possible or no token can be extracted.
    """
    email = os.getenv("DEMO_EMAIL", "customer@practicesoftwaretesting.com")
    password = os.getenv("DEMO_PASSWORD", "welcome01")

    login_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "post" not in ops:
            continue
        if "login" in p.lower():
            login_path = p
            break

    if not login_path:
        pytest.skip("No login endpoint described in OpenAPI spec (cannot run auth tests).")

    url = _absolute(api_base_url, login_path)

    payloads = [
        {"email": email, "password": password},
        {"username": email, "password": password},
        {"login": email, "password": password},
    ]

    for payload in payloads:
        r = http.post(url, json=payload, timeout=DEFAULT_TIMEOUT_SECONDS)
        if r.status_code >= 500:
            continue
        if r.status_code not in (200, 201, 202):
            continue

        try:
            data = r.json()
        except Exception:
            continue

        # Common fields
        for k in ("token", "access_token", "accessToken", "jwt", "bearer"):
            tok = data.get(k) if isinstance(data, dict) else None
            if isinstance(tok, str) and tok.strip():
                return tok.strip()

        # Nested fields
        if isinstance(data, dict):
            for container_key in ("data", "result"):
                inner = data.get(container_key)
                if isinstance(inner, dict):
                    for k in ("token", "access_token", "accessToken", "jwt", "bearer"):
                        tok = inner.get(k)
                        if isinstance(tok, str) and tok.strip():
                            return tok.strip()

    pytest.skip("Login did not return a usable token with DEMO_EMAIL/DEMO_PASSWORD.")