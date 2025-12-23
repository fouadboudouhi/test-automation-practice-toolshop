# User Management Test Automation

Portfolio project to demonstrate senior-level test automation:
- FastAPI REST API + minimal Web UI (only for critical UI tests)
- PostgreSQL (dockerized)
- API tests (pytest) as main quality gate
- UI tests (Playwright) intentionally minimal

## Run locally

```bash
# API quality gate
docker compose run --rm api-tests

# UI quality gate
docker compose run --rm ui-tests
```

## Notes
- DB is truncated before each test to keep tests deterministic.
- Migrations are intentionally skipped at this stage (tables created at startup).
