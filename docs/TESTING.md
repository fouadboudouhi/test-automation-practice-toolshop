# Testing

## Run tests locally

### 1) Start the stack
```bash
make up
```

### 2) Seed DB (required for stable UI runs)
```bash
make seed
```

### 3) UI smoke / regression
```bash
make ui-smoke
make ui-regression
```

Or via the convenience targets:
```bash
make smoke
make regression
```

### 4) Full pipeline
```bash
make test-all
```

---

## Folder structure

### UI tests
- `ui-tests/`
  - `ui-tests/resources/` — shared variables + keywords (single source of truth)
  - `ui-tests/smoke/` — smoke suites
  - `ui-tests/regression/` — regression suites (by feature area)

### API tests
- `api-tests/`
  - `api-tests/tests/smoke/`
  - `api-tests/tests/regression/`
  - `api-tests/conftest.py` — fixtures and shared helpers

---

## Naming conventions

### Robot Framework
- Suite files: `*.robot` named after behavior (e.g. `search_no_results.robot`)
- Keyword naming: **verb-first**, readable (e.g. `Open Toolshop`, `Wait Until Toolshop Ready`)
- Prefer selectors using `data-test` attributes.

### Pytest
- Test file: `test_*.py`
- Test function: `test_*`
- Fixtures: stable names, no hidden global state

---

## Flakiness rules

1) No blind `Sleep` unless you can justify it.
2) Use explicit readiness gates:
   - UI: `Wait Until Toolshop Ready`
   - Product list: `Wait For At Least One Product Card`
3) Retries are allowed only around known-slow UI transitions (`Wait Until Keyword Succeeds`), not to “hide” real issues.
4) Always capture artifacts on failure (Robot `Register Keyword To Run On Failure`).

---

## Reports & artifacts

### UI (Robot)
- `artifacts/ui/<suite>/log.html`
- `artifacts/ui/<suite>/report.html`
- `artifacts/ui/<suite>/output.xml`
- screenshots in `artifacts/ui/<suite>/screenshots/`

### API (Pytest)
- `artifacts/api/<suite>/junit.xml`

