import os
import re

import pytest
import requests


# -----------------------------
# Helpers
# -----------------------------
def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v.strip() if isinstance(v, str) and v.strip() else default


def _absolute(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _unwrap_items(payload):
    """
    Tolerates different pagination wrappers:
    - [ ... ]
    - { "data": [ ... ] }
    - { "data": { "data": [ ... ] } }
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


def _first_identifier(items):
    """Try to extract a usable identifier from a list of dicts."""
    for it in items:
        if not isinstance(it, dict):
            continue
        for k in ("id", "uuid", "ulid", "slug", "code"):
            v = it.get(k)
            if isinstance(v, str | int) and str(v).strip():
                return str(v).strip()
    return None


def _find_list_path(openapi_paths: dict, needle: str) -> str | None:
    """Find a GET collection endpoint like /products (no {id} in path)."""
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


def _find_details_path(openapi_paths: dict, needle: str) -> str | None:
    """Find a GET details endpoint like /products/{id}."""
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
    """Replace the first {...} in a path with value."""
    return re.sub(r"\{[^}]+\}", value, path, count=1)


# -----------------------------
# Session fixtures
# -----------------------------
@pytest.fixture(scope="session")
def http() -> requests.Session:
    s = requests.Session()
    s.headers.update({"accept": "application/json"})
    return s


@pytest.fixture(scope="session")
def api_host() -> str:
    # nginx exposed host (local + CI)
    return _env("API_HOST", "http://localhost:8091").rstrip("/")


@pytest.fixture(scope="session")
def api_docs_url(api_host: str) -> str:
    # Swagger UI HTML page
    return _env("API_DOCS_URL", f"{api_host}/api/documentation")


@pytest.fixture(scope="session")
def openapi_spec_url(http: requests.Session, api_docs_url: str, api_host: str) -> str:
    """
    Extracts the OpenAPI JSON URL from Swagger UI HTML.
    Example you already saw:
      url: "http://localhost:8091/docs?api-docs.json"
    """
    r = http.get(api_docs_url, timeout=30)
    r.raise_for_status()
    m = re.search(r'url:\s*"([^"]+)"', r.text)
    if m:
        return m.group(1)

    # Fallback (best-effort)
    return f"{api_host}/docs?api-docs.json"


@pytest.fixture(scope="session")
def openapi_spec(http: requests.Session, openapi_spec_url: str) -> dict:
    r = http.get(openapi_spec_url, timeout=30)
    r.raise_for_status()
    spec = r.json()
    if not isinstance(spec, dict) or "paths" not in spec:
        raise RuntimeError(
            "OpenAPI spec JSON did not look like an OpenAPI document (missing 'paths')."
        )
    return spec


@pytest.fixture(scope="session")
def openapi_paths(openapi_spec: dict) -> dict:
    return openapi_spec.get("paths", {}) or {}


@pytest.fixture(scope="session")
def openapi(openapi_spec: dict, openapi_paths: dict, openapi_spec_url: str) -> dict:
    """Compatibility fixture (some tests expect `openapi['spec']`)."""
    return {"spec": openapi_spec, "paths": openapi_paths, "spec_url": openapi_spec_url}


@pytest.fixture(scope="session")
def products_list_path(openapi_paths: dict) -> str:
    return _find_list_path(openapi_paths, "products") or "/products"


@pytest.fixture(scope="session")
def categories_list_path(openapi_paths: dict) -> str:
    return _find_list_path(openapi_paths, "categories") or "/categories"


@pytest.fixture(scope="session")
def brands_list_path(openapi_paths: dict) -> str:
    return _find_list_path(openapi_paths, "brands") or "/brands"


@pytest.fixture(scope="session")
def product_details_path(openapi_paths: dict) -> str:
    return _find_details_path(openapi_paths, "products") or "/products/{id}"


@pytest.fixture(scope="session")
def api_base_url(http: requests.Session, api_host: str, products_list_path: str) -> str:
    """
    Some stacks expose endpoints at:
      http://host/products
    others at:
      http://host/api/products

    We auto-detect once per session.
    """
    # probe style A: host + /products
    url_a = _absolute(api_host, products_list_path)
    try:
        ra = http.get(url_a, timeout=15)
        if ra.status_code != 404 and ra.status_code < 500:
            return api_host
    except Exception:
        pass

    # probe style B: host + /api + /products
    api_prefix = api_host + "/api"
    url_b = _absolute(api_prefix, products_list_path)
    try:
        rb = http.get(url_b, timeout=15)
        if rb.status_code != 404 and rb.status_code < 500:
            return api_prefix
    except Exception:
        pass

    raise RuntimeError(
        f"Could not determine API base URL. Probes failed:\n"
        f" - {url_a}\n"
        f" - {url_b}\n"
        f"Check nginx routing or products_list_path."
    )


@pytest.fixture(scope="session")
def sample_product(http: requests.Session, api_base_url: str, products_list_path: str) -> dict:
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
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
    sample_product: dict,
) -> str:
    """
    IMPORTANT: this tries multiple fields (id/slug/uuid/ulid/...) and
    validates by calling the details endpoint until it returns 200.
    """
    candidates = []
    for k in ("id", "slug", "uuid", "ulid", "code"):
        v = sample_product.get(k)
        if isinstance(v, str | int) and str(v).strip():
            candidates.append(str(v).strip())

    if not candidates:
        pytest.skip(
            f"Sample product had no usable identifier fields: keys={list(sample_product.keys())}"
        )

    for cand in candidates:
        path = _replace_first_path_param(product_details_path, cand)
        url = _absolute(api_base_url, path)
        try:
            r = http.get(url, timeout=30)
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
    return _absolute(
        api_base_url, _replace_first_path_param(product_details_path, sample_product_identifier)
    )


@pytest.fixture(scope="session")
def sample_product_id(sample_product_identifier: str) -> str:
    """Alias for older tests that still expect sample_product_id."""
    return sample_product_identifier


@pytest.fixture(scope="session")
def sample_category_id(http: requests.Session, api_base_url: str, categories_list_path: str) -> str:
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=30)
    r.raise_for_status()
    cid = _first_identifier(_unwrap_items(r.json()))
    if not cid:
        pytest.skip("Could not extract a sample category id.")
    return cid


@pytest.fixture(scope="session")
def sample_brand_id(http: requests.Session, api_base_url: str, brands_list_path: str) -> str:
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=30)
    r.raise_for_status()
    bid = _first_identifier(_unwrap_items(r.json()))
    if not bid:
        pytest.skip("Could not extract a sample brand id.")
    return bid


@pytest.fixture(scope="session")
def auth_token(http: requests.Session, api_base_url: str, openapi_paths: dict) -> str:
    """
    Try to login and return a token.
    If your API doesn't support login (or creds are wrong), tests will SKIP.
    """
    email = os.getenv("DEMO_EMAIL", "customer@practicesoftwaretesting.com")
    password = os.getenv("DEMO_PASSWORD", "welcome01")

    login_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "post" not in ops:
            continue
        low = p.lower()
        if "login" in low:
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
        r = http.post(url, json=payload, timeout=30)
        if r.status_code >= 500:
            continue
        if r.status_code not in (200, 201, 202):
            continue

        try:
            data = r.json()
        except Exception:
            continue

        # common fields
        for k in ("token", "access_token", "accessToken", "jwt", "bearer"):
            tok = data.get(k) if isinstance(data, dict) else None
            if isinstance(tok, str) and tok.strip():
                return tok.strip()

        # nested
        if isinstance(data, dict):
            for container_key in ("data", "result"):
                inner = data.get(container_key)
                if isinstance(inner, dict):
                    for k in ("token", "access_token", "accessToken", "jwt", "bearer"):
                        tok = inner.get(k)
                        if isinstance(tok, str) and tok.strip():
                            return tok.strip()

    pytest.skip("Login did not return a usable token with DEMO_EMAIL/DEMO_PASSWORD.")
