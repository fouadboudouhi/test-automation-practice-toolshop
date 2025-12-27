# Testing

## Schnellstart

```bash
make test-all
```

Das startet den Docker-Stack, seeded die DB und führt Smoke + Regression aus.

## Wichtige Targets

- Stack:
  - `make up` / `make down` / `make clean`
- Seed:
  - `make seed`
- API:
  - `make api-smoke`
  - `make api-regression`
- UI:
  - `make ui-smoke`
  - `make ui-regression`

## Headless / Debug

UI-Tests im sichtbaren Browser:

```bash
HEADLESS=false make ui-regression
```

## Reports / Logs

UI-Reports findest du pro Lauf in:

- `artifacts/ui/smoke/run-XXX/`
- `artifacts/ui/regression/run-XXX/`

Wichtige Dateien:
- `report.html`, `log.html`, `output.xml`

API-Reports:
- JUnit XML unter `artifacts/api/.../junit.xml`

## Bekannte App-Route

Der Warenkorb/Checkout ist in dieser App unter:

- `/checkout`

Die gemeinsamen UI-Keywords (Navigation dorthin, Selektoren, etc.) sind in:
- `tests/ui/resources/keywords/common.robot`
