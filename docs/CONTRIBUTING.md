# Contributing

## Adding UI tests (Robot Framework)

Checklist:
1) Put the suite under:
   - `tests/ui/smoke/` for fast gate checks, or
   - `tests/ui/regression/` for deeper coverage
2) Tag the test:
   - `[Tags]    smoke` or `[Tags]    regression`
3) Use `data-test` selectors where possible.
4) Use shared keywords from `tests/ui/resources/` instead of duplicating logic.
5) No raw `Sleep` unless absolutely necessary (prefer readiness keywords).
6) Ensure artifacts are helpful on failure (screenshots, logs).

## Adding API tests (Pytest)

Checklist:
1) Place under `tests/api/smoke/` or `tests/api/regression/`
2) Mark with `@pytest.mark.smoke` / `@pytest.mark.regression`
3) Prefer fixtures from `tests/api/conftest.py`

## PR rules (pragmatic)

Before opening a PR:
- `make smoke` passes locally
- If you touched selectors, you validated them with a real run
- New tests are tagged and placed in correct folders
- Any new env vars are documented in `README.md`

## Commit messages
Keep it short and action-oriented:
- `ui: fix no-results search assertion`
- `ci: randomize ports to avoid conflicts`
- `api: add openapi-driven regression checks`


## Local quality checks

Recommended once:
```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

Then before commits (or anytime):
```bash
pre-commit run -a
```
