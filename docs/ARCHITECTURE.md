# Architecture

## Runtime stack (Docker)

The application under test is started via docker-compose (see `docker/docker-compose.yml`).

Typical services:

- **mariadb**
  - Database for the Laravel API
  - Should be **internal only** (avoid binding 3306 to host to prevent collisions)

- **laravel-api**
  - PHP/Laravel backend
  - Talks to `mariadb`

- **web** (nginx reverse proxy)
  - Exposes the backend routes (e.g. `/api/documentation`) to the host
  - Host port: `${WEB_PORT}` (default: `8091`)
  - Example: `http://localhost:8091/api/documentation`

- **angular-ui**
  - Angular frontend
  - Host port: `${UI_PORT}` (default: `4200`)
  - Example: `http://localhost:4200`

### Why a reverse proxy service?
The UI and API are served behind a single predictable endpoint in local runs, and the API docs endpoint is used as a “readiness gate” for tests.

---

## Test stack overview

### UI tests (Robot Framework)
- Tooling: Robot Framework + `robotframework-browser` (Playwright)
- Location: `ui-tests/`
- Tagging:
  - `smoke` → fast checks used as a gate
  - `regression` → deeper coverage

### API tests (Pytest)
- Tooling: Pytest + `requests`
- Location: `api-tests/`
- Tagging:
  - `smoke` → fast endpoint sanity checks
  - `regression` → deeper contract-like checks driven by OpenAPI

---

## Data & Seeding

Before UI/API tests run, the DB is migrated + seeded:

- `php artisan migrate:fresh --seed`
- Verification step checks product count > 0 to ensure the UI has content.

---

## Artifacts

- UI: Robot outputs (`log.html`, `report.html`, `output.xml`) and screenshots
- API: `junit.xml` for CI reporting

Standard output location: `artifacts/`
