from urllib.parse import urlencode

import pytest
import requests


def _absolute(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _unwrap_list_payload(data):
    """
    Supports list OR {data:[...]} OR {data:{data:[...]}}.
    Returns list or None.
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
    kw = keyword.lower()
    for p, ops in openapi_paths.items():
        if kw in p.lower() and "{" not in p and isinstance(ops, dict) and "get" in ops:
            return p
    return None


@pytest.mark.smoke
def test_swagger_ui_is_reachable(http: requests.Session, api_docs_url: str):
    r = http.get(api_docs_url, timeout=30)
    assert r.status_code == 200
    # Swagger UI is HTML
    assert "<title" in r.text.lower()


@pytest.mark.smoke
def test_openapi_spec_is_loadable(openapi_spec: dict):
    assert isinstance(openapi_spec, dict)
    assert "paths" in openapi_spec and openapi_spec["paths"]


@pytest.mark.smoke
def test_products_list_returns_200(
    http: requests.Session, api_base_url: str, products_list_path: str
):
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())


@pytest.mark.smoke
def test_products_list_is_not_empty(
    http: requests.Session, api_base_url: str, products_list_path: str
):
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
    assert r.status_code == 200
    items = _unwrap_list_payload(r.json())
    assert isinstance(items, list)
    assert len(items) > 0


@pytest.mark.smoke
def test_product_details_for_first_item(http: requests.Session, sample_product_details_url: str):
    # This URL is resolved robustly in conftest.py by probing identifiers until 200.
    r = http.get(sample_product_details_url, timeout=30)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())
    data = r.json()
    assert isinstance(data, dict | list)


@pytest.mark.smoke
def test_categories_list_returns_200(
    http: requests.Session, api_base_url: str, categories_list_path: str
):
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=30)
    assert r.status_code == 200


@pytest.mark.smoke
def test_brands_list_returns_200(http: requests.Session, api_base_url: str, brands_list_path: str):
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=30)
    assert r.status_code == 200


@pytest.mark.smoke
def test_products_endpoint_supports_pagination_if_described(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
):
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
    r = http.get(url, timeout=30)
    assert r.status_code == 200


@pytest.mark.smoke
def test_filter_products_by_category_param_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_product: dict,
):
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
        pytest.skip(
            "No category filter parameter described for products list endpoint in OpenAPI spec"
        )

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
    r = http.get(url, timeout=30)
    assert r.status_code == 200


@pytest.mark.smoke
def test_filter_products_by_brand_param_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_product: dict,
):
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
        pytest.skip(
            "No brand filter parameter described for products list endpoint in OpenAPI spec"
        )

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
    r = http.get(url, timeout=30)
    assert r.status_code == 200
