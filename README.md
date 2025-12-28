# Test Automation Practice — Toolshop (Sprint 5)

A production-like **test automation harness** around the “Toolshop” demo application (Practice Software Testing, Sprint 5),
built to showcase **Dockerized environments**, **repeatable local workflows**, **CI pipelines**, **functional testing**
(UI + API), and **load testing (k6)**.

This repository is intentionally structured like a real-world QA/DevEx project:
- one command to bring the stack up,
- deterministic seeding,
- smoke vs regression test separation,
- standardized artifacts and evidence.

---

## What’s inside

- **Docker Compose stack**: UI + API + DB + reverse proxy (API gateway).
- **Makefile** as the single entry point for local workflows.
- **UI tests** using Robot Framework + Browser (Playwright).
- **API tests** using pytest + requests (OpenAPI-aware checks).
- **Load tests** using k6 (smoke, ramp, peak, soak).
- **Artifacts** saved under `artifacts/` for CI-friendly evidence.

---

## Quick start

### Prerequisites
- Docker + Docker Compose v2
- GNU Make
- Python **3.11**
- `rfbrowser` prerequisites: Robot Framework Browser uses Playwright (installed via `rfbrowser init`)

### 1) Create a virtualenv and install dependencies
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
# Optional (lint/type tooling)
pip install -r requirements-dev.txt
```

### 2) Install Browser library dependencies (Playwright)
```bash
rfbrowser init
```

### 3) Bring the stack up
```bash
make up
```

Default endpoints:
- UI: `http://localhost:4200`
- API gateway / docs: `http://localhost:8091/api/documentation`

### 4) Seed the database
```bash
make seed
```

### 5) Run tests
Smoke:
```bash
make smoke
```

Regression:
```bash
make regression
```

Full local pipeline:
```bash
make test-all
```

---

## Main commands

- `make up` / `make down` / `make clean`
- `make seed` (waits for API + DB, runs migrate/seed, verifies product count)
- `make ui-smoke` / `make ui-regression`
- `make api-smoke` / `make api-regression`
- `make k6-smoke` / `make k6-ramp` / `make k6-peak` / `make k6-soak`

---

## Configuration

All important settings can be overridden via environment variables (examples):

```bash
# change ports and compose project isolation
COMPOSE_PROJECT_NAME=toolshop-e2e-2 WEB_PORT=8092 UI_PORT=4201 make test-all

# UI execution
HEADLESS=false make ui-smoke

# API coverage (optional)
COV=true COV_FAIL_UNDER=60 make api-smoke
```

---

## Artifacts and evidence

This repo writes all evidence into deterministic folders:

- UI: `artifacts/ui/smoke/run-XXX/` and `artifacts/ui/regression/run-XXX/`
- API: `artifacts/api/smoke/` and `artifacts/api/regression/`
- k6: `artifacts/k6/<scenario>/run-XXX/`

Open the most recent UI report locally:
```bash
make ui-open-latest
```

---

## Documentation

- `docs/ARCHITECTURE.md` — system overview and how components interact
- `docs/TESTING.md` — how to run/debug tests locally and in CI-like conditions
- `docs/TESTPLAN.md` — interview-grade test plan and test inventory

---

## Notes / known demo limitations

This project tests a **demo application**. Some endpoints/behaviors may not match the OpenAPI contract perfectly.
When that happens, the tests try to:
- prefer contract-derived values,
- fail with actionable debug output,
- and keep skips for endpoints that cannot be tested in the current gateway shape.

If you see a consistent 5xx on sorting (e.g. `GET /products?sort=...`), that indicates an **AUT issue or contract mismatch** rather than flaky automation.

---

## Repository structure

```text
.
  .gitignore
  Makefile
  README.md
  pyproject.toml
  pytest.ini
  requirements-dev.txt
  requirements.txt
artifacts/
  k6/
    smoke/
      summary.json
    peak/
      run-001/
        summary.json
    ramp/
      run-001/
        summary.json
docker/
  README.md
  docker-compose.yml
  nginx/
    default.conf
.pytest_cache/
  .gitignore
  CACHEDIR.TAG
  README.md
  v/
    cache/
      lastfailed
      nodeids
.ruff_cache/
  .gitignore
  CACHEDIR.TAG
  0.8.4/
    10352653465989691370
    13718451130533832589
    14543009357150214380
    15615112839415525973
    6135972462602005084
    7697044981311104874
tests/
  ui/
    smoke/
      categories_dropdown.robot
      contact_route.robot
      filters_panel_has_brands.robot
      filters_panel_has_categories.robot
      home.robot
      login.robot
      login_page_fields.robot
      navigation.robot
      privacy_route.robot
      product.robot
      product_details_add_to_cart_visible.robot
      products_have_images.robot
      products_have_prices.robot
      products_route.robot
      search.robot
    resources/
      keywords/
        common.robot
    regression/
      filters/
        clear_brand_filter.robot
        filter_by_brand.robot
        filter_by_category.robot
      products/
        back_to_products_after_details.robot
        details_has_add_to_cart.robot
        direct_products_access.robot
        open_first_product_details.robot
        open_two_products_titles_differ.robot
        product_image_src_not_empty.robot
      navigation/
        categories_dropdown_entries.robot
        contact_page_form_present.robot
        privacy_page_heading.robot
      search/
        clear_search_restores_products.robot
        no_results_empty_or_message.robot
        search_results.robot
      sorting/
        sort_by_price.robot
      cart/
        add_to_cart.robot
        cart_contains_added_product.robot
        cart_persists_after_reload.robot
      login/
        negative_login.robot
  api/
    conftest.py
    smoke/
      test_api_smoke.py
    regression/
      test_api_regression.py
docs/
  ARCHITECTURE.md
  CI.md
  CONTRIBUTING.md
  TESTING.md
  TESTPLAN.md
load/
  k6/
    peak.js
    ramp.js
    smoke.js
    soak.js
.venv/
  .gitignore
  CACHEDIR.TAG
  pyvenv.cfg
  bin/
    activate
    activate.csh
    activate.fish
    activate.nu
    activate.ps1
    activate_this.py
    fastapi
    normalizer
    pip
    pip3
    pip3.13
    playwright
    py.test
    pygmentize
    pytest
    python
    python3
    python3.13
    ...
```
