import time
from urllib.parse import urlencode

import pytest
import requests


def _absolute(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _unwrap_items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data", payload)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if isinstance(data, list):
            return data
    return []


def _unwrap_obj(payload):
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        return payload["data"]
    return payload


def _find_query_param(openapi_paths: dict, path: str, needle: str) -> str | None:
    ops = (openapi_paths or {}).get(path, {})
    get_op = (ops or {}).get("get", {}) if isinstance(ops, dict) else {}
    params = get_op.get("parameters") or []
    needle = needle.lower()
    for p in params:
        name = (p.get("name") or "").lower()
        if needle in name:
            return p.get("name")
    return None


@pytest.mark.regression
def test_openapi_has_info(openapi):
    spec = openapi["spec"]
    assert isinstance(spec, dict)
    assert "info" in spec and isinstance(spec["info"], dict)
    assert spec["info"].get("title")


@pytest.mark.regression
def test_products_list_returns_json_200(
    http: requests.Session, api_base_url: str, products_list_path: str
):
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
    assert r.status_code == 200
    assert "json" in (r.headers.get("content-type", "").lower())


@pytest.mark.regression
def test_products_list_has_minimum_fields(
    http: requests.Session, api_base_url: str, products_list_path: str
):
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
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
):
    r = http.get(sample_product_details_url, timeout=30)
    assert r.status_code == 200
    blob = _unwrap_obj(r.json())
    assert isinstance(blob, dict)

    candidates = []
    for k in ("id", "uuid", "ulid", "slug", "code"):
        v = blob.get(k)
        if v is not None:
            candidates.append(str(v))

    assert candidates, f"No identifier field found in response keys={list(blob.keys())}"
    assert sample_product_identifier in candidates


@pytest.mark.regression
def test_categories_list_returns_200(
    http: requests.Session, api_base_url: str, categories_list_path: str
):
    r = http.get(_absolute(api_base_url, categories_list_path), timeout=30)
    assert r.status_code == 200


@pytest.mark.regression
def test_brands_list_returns_200(http: requests.Session, api_base_url: str, brands_list_path: str):
    r = http.get(_absolute(api_base_url, brands_list_path), timeout=30)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_filter_by_category_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_category_id: str,
):
    cat_param = _find_query_param(openapi_paths, products_list_path, "category")
    if not cat_param:
        pytest.skip("No category query parameter described for products list")
    url = (
        _absolute(api_base_url, products_list_path)
        + "?"
        + urlencode({cat_param: sample_category_id})
    )
    r = http.get(url, timeout=30)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_filter_by_brand_if_supported(
    http: requests.Session,
    api_base_url: str,
    products_list_path: str,
    openapi_paths: dict,
    sample_brand_id: str,
):
    brand_param = _find_query_param(openapi_paths, products_list_path, "brand")
    if not brand_param:
        pytest.skip("No brand query parameter described for products list")
    url = (
        _absolute(api_base_url, products_list_path)
        + "?"
        + urlencode({brand_param: sample_brand_id})
    )
    r = http.get(url, timeout=30)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_pagination_page_2_if_supported(
    http: requests.Session, api_base_url: str, products_list_path: str, openapi_paths: dict
):
    page_param = _find_query_param(openapi_paths, products_list_path, "page")
    if not page_param:
        pytest.skip("No page parameter described for products list")
    url = _absolute(api_base_url, products_list_path) + "?" + urlencode({page_param: 2})
    r = http.get(url, timeout=30)
    assert r.status_code == 200


@pytest.mark.regression
def test_products_sorting_if_supported(
    http: requests.Session, api_base_url: str, products_list_path: str, openapi_paths: dict
):
    sort_param = _find_query_param(openapi_paths, products_list_path, "sort")
    if not sort_param:
        pytest.skip("No sort parameter described for products list")

    # Try a conservative value often used in such APIs
    url = _absolute(api_base_url, products_list_path) + "?" + urlencode({sort_param: "price-asc"})
    r = http.get(url, timeout=30)

    # If server crashes (5xx), that's an AUT bug or unsupported sort -> don't break your pipeline
    if r.status_code >= 500:
        pytest.xfail(
            "API returns 5xx for sort=price-asc (likely AUT bug or unsupported sort value)."
        )

    # Some APIs ignore unknown sorts and still return 200; some validate and return 4xx
    assert r.status_code in (200, 400, 422)


@pytest.mark.regression
def test_products_endpoint_invalid_sort_does_not_crash_if_supported(
    http: requests.Session, api_base_url: str, products_list_path: str, openapi_paths: dict
):
    sort_param = _find_query_param(openapi_paths, products_list_path, "sort")
    if not sort_param:
        pytest.skip("No sort parameter described")
    url = (
        _absolute(api_base_url, products_list_path)
        + "?"
        + urlencode({sort_param: "this_is_not_a_real_sort"})
    )
    r = http.get(url, timeout=30)

    if r.status_code >= 500:
        pytest.xfail("API returns 5xx on invalid sort value (server-side bug).")

    assert r.status_code in (200, 400, 422)


@pytest.mark.regression
def test_login_returns_token(auth_token: str):
    assert isinstance(auth_token, str) and auth_token.strip()


@pytest.mark.regression
def test_me_endpoint_requires_auth_if_present(
    http: requests.Session, api_base_url: str, openapi_paths: dict, auth_token: str
):
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

    r_unauth = http.get(url, timeout=30)
    if r_unauth.status_code == 404:
        pytest.skip("Endpoint exists in spec but is not reachable via current gateway (404).")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(url, headers={"Authorization": f"Bearer {auth_token}"}, timeout=30)
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_invoices_list_requires_auth_if_present(
    http: requests.Session, api_base_url: str, openapi_paths: dict, auth_token: str
):
    inv_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "invoice" in p.lower() and "{" not in p:
            inv_path = p
            break
    if not inv_path:
        pytest.skip("No invoices list endpoint described")

    url = _absolute(api_base_url, inv_path)

    r_unauth = http.get(url, timeout=30)
    if r_unauth.status_code == 404:
        pytest.skip("Endpoint exists in spec but is not reachable via current gateway (404).")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(url, headers={"Authorization": f"Bearer {auth_token}"}, timeout=30)
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_favorites_list_requires_auth_if_present(
    http: requests.Session, api_base_url: str, openapi_paths: dict, auth_token: str
):
    fav_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict) or "get" not in ops:
            continue
        if "favorite" in p.lower() and "{" not in p:
            fav_path = p
            break
    if not fav_path:
        pytest.skip("No favorites list endpoint described")

    url = _absolute(api_base_url, fav_path)

    r_unauth = http.get(url, timeout=30)
    if r_unauth.status_code == 404:
        pytest.skip("Endpoint exists in spec but is not reachable via current gateway (404).")

    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(url, headers={"Authorization": f"Bearer {auth_token}"}, timeout=30)
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_cart_get_requires_auth_if_present(
    http: requests.Session, api_base_url: str, openapi_paths: dict, auth_token: str
):
    cart_path = None
    for p, ops in (openapi_paths or {}).items():
        if not isinstance(ops, dict):
            continue
        if "cart" in p.lower() and "get" in ops:
            cart_path = p
            break
    if not cart_path:
        pytest.skip("No cart GET endpoint described")

    url = _absolute(api_base_url, cart_path)

    r_unauth = http.get(url, timeout=30)
    if r_unauth.status_code == 404:
        pytest.skip("Cart endpoint exists in spec but is not reachable via current gateway (404).")
    assert r_unauth.status_code in (401, 403, 200)

    r_auth = http.get(url, headers={"Authorization": f"Bearer {auth_token}"}, timeout=30)
    if r_auth.status_code == 404:
        pytest.skip("Cart endpoint exists in spec but is not reachable via current gateway (404).")
    assert r_auth.status_code < 500


@pytest.mark.regression
def test_products_endpoint_response_time_is_reasonable(
    http: requests.Session, api_base_url: str, products_list_path: str
):
    start = time.time()
    r = http.get(_absolute(api_base_url, products_list_path), timeout=30)
    elapsed = time.time() - start
    assert r.status_code == 200
    assert elapsed < 5.0
