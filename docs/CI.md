# CI

This repo uses GitHub Actions to run UI tests against a Dockerized stack.

Workflows:
- `ci-ui-tests.yml` (Docker stack + Smoke/Regression)
- `quality.yml` (lint/format/typecheck/security)
- `dependency-review.yml` (GitHub dependency review on PRs)

---

## When it runs
- On push to `main`
- On pull requests targeting `main`

---

## Gating strategy
- **Smoke** job is the quality gate (“QGate”).
- **Regression** runs **only if smoke succeeds**.

This keeps feedback fast and avoids burning CI time on a broken build.

---

## CI design notes

### Port collision avoidance
In CI, we publish **random host ports** for:
- `web` (nginx on port 80 inside container)
- `angular-ui` (4200 inside container)

Then CI detects the mapped ports using:
- `docker compose port web 80`
- `docker compose port angular-ui 4200`

And exports:
- `API_HOST=http://localhost:<web_port>`
- `API_DOCS_URL=http://localhost:<web_port>/api/documentation`
- `API_DOC_URL=http://localhost:<web_port>/api/documentation` (deprecated alias)
- `BASE_URL=http://localhost:<ui_port>`

This prevents conflicts across jobs and makes the workflow more robust.

### Database seeding
CI always:
1) Waits for DB healthy
2) Runs migrations + seed
3) Verifies product count > 0

---

## Caching
- Python dependencies: `actions/setup-python` with `cache: pip`
- Playwright browsers: cached under `~/.cache/ms-playwright`

---

## Typical CI failures and fixes

### API docs endpoint never becomes reachable
- Check docker logs from the `web` and `laravel-api` containers.
- Often indicates DB not ready or migrations not executed.

### UI reachable but tests fail on selectors/timeouts
- Most often:
  - seed step failed (no products → UI empty)
  - selector mismatch (prefer `data-test`)
  - CI slower than local (use readiness gates and targeted retries)

### Artifact debugging
Always inspect uploaded Robot artifacts:
- `log.html` is the first stop
- `report.html` gives the suite overview
- `output.xml` is machine-readable


---

## Coverage gate (API)

CI runs API smoke/regression with `pytest-cov` and enforces a minimal coverage threshold (`--cov-fail-under`).
Coverage XML is uploaded with the other artifacts under:
- `artifacts/api/smoke/coverage.xml`
- `artifacts/api/regression/coverage.xml`
