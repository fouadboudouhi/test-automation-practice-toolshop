# Test Plan

This test plan is written for interview discussions: it explains **scope, strategy, and the full test inventory**.

## 1. Objectives

- Provide fast confidence that the Toolshop demo application is reachable and stable.
- Validate key user journeys (filters, search, product details, cart).
- Validate API endpoints against the published OpenAPI contract where possible.
- Provide performance signals via k6 scenarios (smoke, ramp, peak, soak).

## 2. Scope

**In scope**
- UI: navigation, product listing, filters, search, product details, cart flows
- API: catalog endpoints, authentication endpoints (where present), contract-driven optional features
- Load: read-heavy catalog flows plus auth-dependent probes

**Out of scope**
- Visual regression / pixel-perfect UI checks
- Deep security testing (beyond basic auth guards)
- Browser matrix (tests are designed to run on Chromium in CI)

## 3. Test levels and execution

- **Smoke**: fast checks, intended for every PR.
- **Regression**: deeper coverage, intended for main branch and scheduled runs.
- **Load**: scenario-driven; scheduled or manual depending on duration.

## 4. Test inventory

### 4.1 UI tests (Robot Framework)

#### UI Regression — Cart

- **Add Product To Cart** (`tests/ui/regression/cart/add_to_cart.robot`)
  - Purpose: Regression test for add-to-cart functionality. Expected to expose known demo application issues.
- **Cart Contains Added Product Name** (`tests/ui/regression/cart/cart_contains_added_product.robot`)
  - Purpose: Regression: add product to cart and verify it is shown in cart.
- **Cart Persists After Reload** (`tests/ui/regression/cart/cart_persists_after_reload.robot`)
  - Purpose: Regression: cart content persists after reload.

#### UI Regression — Filters

- **Clear Brand Filter Restores Results** (`tests/ui/regression/filters/clear_brand_filter.robot`)
  - Purpose: Regression: apply and clear brand filter; list should still show results.
- **Filter Products By Brand** (`tests/ui/regression/filters/filter_by_brand.robot`)
  - Purpose: Regression: apply a brand filter (if available) and ensure results still show.
- **Filter Products By Category** (`tests/ui/regression/filters/filter_by_category.robot`)
  - Purpose: Regression test for category filtering.

#### UI Regression — Login

- **Login With Invalid Credentials** (`tests/ui/regression/login/negative_login.robot`)
  - Purpose: Regression test for invalid login handling. Verifies that an error message is shown for invalid credentials.

#### UI Regression — Navigation

- **Categories Dropdown Contains Entries** (`tests/ui/regression/navigation/categories_dropdown_entries.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Contact Page Has A Form** (`tests/ui/regression/navigation/contact_page_form_present.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Privacy Page Shows Heading** (`tests/ui/regression/navigation/privacy_page_heading.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.

#### UI Regression — Products

- **Navigate Back To Products From Details** (`tests/ui/regression/products/back_to_products_after_details.robot`)
  - Purpose: Regression: navigate back after opening product details.
- **Product Details Has Add To Cart Button** (`tests/ui/regression/products/details_has_add_to_cart.robot`)
  - Purpose: Regression: product details shows Add to cart.
- **Direct Access To Products Route Works** (`tests/ui/regression/products/direct_products_access.robot`)
  - Purpose: Regression: products listing is reachable (home shows products).
- **Open First Product Details** (`tests/ui/regression/products/open_first_product_details.robot`)
  - Purpose: Regression: open first product details from product listing (home).
- **Two Different Products Have Different Titles** (`tests/ui/regression/products/open_two_products_titles_differ.robot`)
  - Purpose: Regression: two different products have different titles on the listing.
- **Product Card Image Src Is Not Empty** (`tests/ui/regression/products/product_image_src_not_empty.robot`)
  - Purpose: Regression: first product card image src is not empty.

#### UI Regression — Search

- **Clearing Search Restores Product List** (`tests/ui/regression/search/clear_search_restores_products.robot`)
  - Purpose: Regression: search then clear search and products are shown again.
- **Search With No Results Shows No Products Message** (`tests/ui/regression/search/no_results_empty_or_message.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Search Returns Matching Products** (`tests/ui/regression/search/search_results.robot`)
  - Purpose: Regression test for search functionality.

#### UI Regression — Sorting

- **Sort Products By Price** (`tests/ui/regression/sorting/sort_by_price.robot`)
  - Purpose: Regression test for sorting products by price.

#### UI Smoke

- **Categories Dropdown Opens** (`tests/ui/smoke/categories_dropdown.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Contact Page Is Reachable** (`tests/ui/smoke/contact_route.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Filters Show Brand Options** (`tests/ui/smoke/filters_panel_has_brands.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Filters Show Category Options** (`tests/ui/smoke/filters_panel_has_categories.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Homepage Is Reachable** (`tests/ui/smoke/home.robot`)
  - Purpose: Smoke test verifying that the homepage is reachable.
- **Login Is Possible** (`tests/ui/smoke/login.robot`)
  - Purpose: Smoke test verifying that login is possible.
- **Login Page Shows Required Fields** (`tests/ui/smoke/login_page_fields.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Navigation Is Visible** (`tests/ui/smoke/navigation.robot`)
  - Purpose: Smoke test verifying that navigation is present.
- **Privacy Page Is Reachable** (`tests/ui/smoke/privacy_route.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Product Page Is Reachable** (`tests/ui/smoke/product.robot`)
  - Purpose: Smoke test verifying that at least one product card is visible.
- **Product Details Shows Add To Cart** (`tests/ui/smoke/product_details_add_to_cart_visible.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Product Thumbnails Are Visible** (`tests/ui/smoke/products_have_images.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Product Cards Show A Price** (`tests/ui/smoke/products_have_prices.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Products Route Is Reachable** (`tests/ui/smoke/products_route.robot`)
  - Purpose: No suite-level documentation found; intent inferred from the test name and location.
- **Search Field Is Available** (`tests/ui/smoke/search.robot`)
  - Purpose: Smoke test verifying that search is present.

### 4.2 API tests (pytest)

#### API Smoke

- **test_swagger_ui_is_reachable**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_openapi_spec_is_loadable**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_products_list_returns_200**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_products_list_is_not_empty**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_product_details_for_first_item**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_categories_list_returns_200**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_brands_list_returns_200**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_products_endpoint_supports_pagination_if_described**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_filter_products_by_category_param_if_supported**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.
- **test_filter_products_by_brand_param_if_supported**
  - Purpose: Fast reachability and basic contract sanity for key catalog endpoints.

#### API Regression

- **test_openapi_has_info**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_products_list_returns_json_200**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_products_list_has_minimum_fields**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_product_details_endpoint_returns_same_identifier**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_categories_list_returns_200**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_brands_list_returns_200**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_products_filter_by_category_if_supported**
  - Purpose: Exercise filtering behavior if described by OpenAPI.
- **test_products_filter_by_brand_if_supported**
  - Purpose: Exercise filtering behavior if described by OpenAPI.
- **test_products_pagination_page_2_if_supported**
  - Purpose: Exercise pagination behavior if described by OpenAPI.
- **test_products_sorting_if_supported**
  - Purpose: Exercise sorting behavior if described by OpenAPI and ensure it does not trigger 5xx.
- **test_products_endpoint_invalid_sort_does_not_crash_if_supported**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_login_returns_token**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.
- **test_me_endpoint_requires_auth_if_present**
  - Purpose: Validate authentication / authorization expectations for protected endpoints.
- **test_invoices_list_requires_auth_if_present**
  - Purpose: Validate authentication / authorization expectations for protected endpoints.
- **test_favorites_list_requires_auth_if_present**
  - Purpose: Validate authentication / authorization expectations for protected endpoints.
- **test_cart_get_requires_auth_if_present**
  - Purpose: Validate authentication / authorization expectations for protected endpoints.
- **test_products_endpoint_response_time_is_reasonable**
  - Purpose: Validate endpoint behavior and minimal response shape/contract expectations.

### 4.3 Load tests (k6)

- **smoke** (`load/k6/smoke.js`)
  - Goal: short, low-risk run to validate basic stability under small concurrent load.
- **ramp** (`load/k6/ramp.js`)
  - Goal: capacity trend by ramping VUs up, holding, and ramping down.
- **peak** (`load/k6/peak.js`)
  - Goal: spike/peak traffic simulation to observe error rates and latency under bursts.
- **soak** (`load/k6/soak.js`)
  - Goal: longer run to detect slow leaks (resources, connection pools, memory).

## 5. Exit criteria

- Smoke suite passes on PRs.
- Regression suite passes on main branch (or known demo issues are documented and triaged).
- Load tests produce `summary.json` and stay within agreed thresholds (if defined).

## 6. Evidence

- UI: `log.html`, `report.html`, screenshots (on failure) under `artifacts/ui/...`
- API: JUnit XML (and optional coverage) under `artifacts/api/...`
- Load: `summary.json` under `artifacts/k6/...`
