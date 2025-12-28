# Architecture

This repository is a **test automation harness** around a dockerized Toolshop demo application.
The core design goals are:

- **Deterministic local workflow** via `make ...` (same steps as CI)
- **Clear separation** of UI / API / load testing
- **Evidence-first**: every run produces artifacts suitable for CI and debugging
- **Minimal coupling** to implementation details; prefer public HTTP contracts and stable selectors

---

## High-level diagram (runtime + tooling)

```text
                         ┌───────────────────────────┐
                         │   Developer / CI Runner   │
                         │  (Make, Python, Robot, k6)│
                         └──────────────┬────────────┘
                                        │
                                        │ make up / seed / tests
                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         Docker Compose stack                          │
│                                                                       │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐  │
│   │  angular-ui  │     │     web      │     │     laravel-api      │  │
│   │  (UI :4200)  │     │ (nginx :80)  │     │ (PHP-FPM :9000)      │  │
│   └──────┬───────┘     └──────┬───────┘     └────────────┬─────────┘  │
│          │                    │                          │            │
│          │ UI tests hit UI    │ API tests hit gateway    │ DB access  │
│          │                    │                          │            │
│          │                    ▼                          ▼            │
│          │            http://localhost:8091        ┌──────────────┐   │
│          │                                         │   mariadb    │   │
│          │                                         │ (DB service) │   │
│          │                                         └──────────────┘   │
│          │                                                            │
│   UI runner: Robot + Browser (Playwright)                             │
│   API runner: pytest + requests (OpenAPI-aware probes)                │
│   Load runner: k6 scenarios (smoke/ramp/peak/soak)                    │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Components

### Docker Compose services

The Compose file defines these main services:

- **`angular-ui`** — Toolshop frontend (Angular). Exposed on `${UI_PORT:-4200}`.
- **`web`** — Nginx gateway. Exposed on `${WEB_PORT:-8091}`. Serves API/docs endpoints via the gateway.
- **`laravel-api`** — Toolshop backend (Laravel / PHP-FPM), connected to the DB service.
- **`mariadb`** — persistence layer; used by seeding and runtime.
- **`laravel-app-code`** — a volume/service used to share app code into containers (depending on image layout).

### Makefile: the “single interface”

The Makefile intentionally acts as the **single source of truth** for workflows:
- health waiting (`wait-ui`, `wait-api`, `wait-db`)
- seeding and verification
- test runs (UI/API)
- standardized artifact directory layout
- k6 scenario runners and parameterization

This reduces CI drift: CI simply runs `make ...` targets.

### Test taxonomy

- **Smoke tests**: fast checks to prove the system is up (routing, critical UI elements, basic API reachability).
- **Regression tests**: deeper functional scenarios (filters, cart behavior, sorting, OpenAPI contract checks).
- **Load tests**: capacity and stability probes (smoke/ramp/peak/soak).

---

## Key data flows

### Seeding
1. `make seed` waits for API + DB
2. Runs `php artisan migrate:fresh --seed` in `laravel-api`
3. Verifies DB state via SQL (`SELECT COUNT(*) FROM products;`)

### UI tests
- Implemented in Robot Framework.
- Browser Library runs Playwright.
- “Strict mode” safe selectors are used where possible (`>> nth=0` or XPath first match).

### API tests
- Implemented in pytest.
- Tests use the OpenAPI docs endpoint to discover and validate behaviors where supported (pagination/filter/sort).
- When contract features are absent, tests skip instead of failing.

### Load tests (k6)
- Scenarios are plain JS (`load/k6/*.js`).
- Output is exported as `summary.json` into `artifacts/k6/<scenario>/run-XXX/`.

---

## Directory conventions

- `.github/workflows/` — CI (functional + load)
- `docker/` — compose + nginx config
- `tests/ui/` — Robot UI tests (+ resources/keywords)
- `tests/api/` — pytest suites (smoke + regression)
- `load/k6/` — k6 scenarios
- `artifacts/` — all runtime evidence and CI outputs
