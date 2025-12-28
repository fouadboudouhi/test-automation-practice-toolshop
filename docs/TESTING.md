# Testing Guide

This document explains how to run and debug tests locally in a CI-like way.

---

## Prerequisites

- Docker + Docker Compose v2
- Make
- Python 3.11
- Robot Framework Browser prerequisites:
  - Install Python deps
  - Run `rfbrowser init` once (installs Playwright + browsers)

---

## Environment variables

Common:
- `BASE_URL` (default `http://localhost:4200`)
- `API_HOST` (default `http://localhost:8091`)
- `API_DOCS_URL` (default `${API_HOST}/api/documentation`)
- `HEADLESS` (`true`/`false`) for UI tests

Credentials (optional; defaults exist in keywords):
- `DEMO_EMAIL`
- `DEMO_PASSWORD`

Ports:
- `WEB_PORT` (API gateway)
- `UI_PORT` (frontend)

---

## Bring up the stack

```bash
make up
make seed
```

Health checks:
```bash
make wait-ui
make wait-api
make wait-db
```

---

## UI tests (Robot Framework)

### Install Browser dependencies
```bash
rfbrowser init
```

### Run UI smoke
```bash
make ui-smoke
```

### Run UI regression
```bash
make ui-regression
```

### Artifacts
Each run is stored under:
- `artifacts/ui/smoke/run-XXX/`
- `artifacts/ui/regression/run-XXX/`

Robot outputs typically include:
- `output.xml`
- `log.html`
- `report.html`

Open latest locally:
```bash
make ui-open-latest
```

### Debugging tips
- Run with `HEADLESS=false` to see the browser:
  ```bash
  HEADLESS=false make ui-smoke
  ```
- If selectors fail due to strict-mode, prefer:
  - `>> nth=0` for first match
  - XPath first match for some menus

---

## API tests (pytest)

### Run API smoke
```bash
make api-smoke
```

### Run API regression
```bash
make api-regression
```

Artifacts:
- JUnit XML: `artifacts/api/<suite>/junit.xml`
- Optional coverage (when enabled): `coverage.xml`

### Coverage (optional)
```bash
COV=true COV_FAIL_UNDER=60 make api-smoke
```

### Debugging tips
- Re-run a single test:
  ```bash
  API_HOST=http://localhost:8091 python -m pytest -vv tests/api/regression/test_api_regression.py -k sorting
  ```
- If an endpoint returns 5xx for valid inputs (e.g. sorting), treat it as:
  - AUT crash, or
  - contract mismatch
  In either case, keep evidence (response snippet + service logs).

---

## Load tests (k6)

Scenarios:
- `k6-smoke` — short run, low VUs
- `k6-ramp` — ramp up / hold / ramp down
- `k6-peak` — spike style run
- `k6-soak` — long run

Examples:
```bash
make k6-smoke K6_VUS=10 K6_DURATION=1m
make k6-ramp  K6_RAMP_TARGET=40 K6_RAMP_UP=3m K6_RAMP_HOLD=5m K6_RAMP_DOWN=2m
make k6-peak  K6_PEAK_VUS=75 K6_PEAK_RAMP_UP=30s K6_PEAK_HOLD=60s K6_PEAK_RAMP_DOWN=30s
make k6-soak  K6_SOAK_VUS=10 K6_SOAK_DURATION=30m
```

Artifacts:
- `artifacts/k6/<scenario>/run-XXX/summary.json`

---

## CI parity

To reproduce CI locally, prefer:
```bash
make test-all
```

This runs:
1. `make up`
2. `make seed`
3. `make smoke`
4. `make regression`
