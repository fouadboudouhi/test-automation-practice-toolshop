# Testplan

Ziel: Mit einer **Smoke-Suite** schnell Vertrauen gewinnen und mit einer **Regression-Suite** breiter absichern.

## Smoke

### API Smoke (pytest)
- Pfad: `tests/api/smoke/test_api_smoke.py`
- Ziel:
  - API erreichbar
  - Grundlegende Endpunkte liefern sinnvolle Antworten
- Ausführung:
  ```bash
  make api-smoke
  ```

### UI Smoke (Robot)
- Pfad: `tests/ui/smoke/`
- Ziel:
  - UI erreichbar
  - Navigation vorhanden
  - Login möglich
  - Produktliste sichtbar (mindestens eine Karte)
- Ausführung:
  ```bash
  make ui-smoke
  ```

## Regression

### API Regression (pytest)
- Pfad: `tests/api/regression/test_api_regression.py`
- Ziel:
  - Breitere Abdeckung (Filter, Suche, Edge-Cases)
  - Robustheit gegen ungültige Inputs (wo sinnvoll)
- Ausführung:
  ```bash
  make api-regression
  ```

### UI Regression (Robot)
- Pfad: `tests/ui/regression/`
- Ziel:
  - Kern-Userflows (z. B. Add-to-Cart/Checkout)
  - Filter / Sorting / Search
  - Navigationsseiten (Privacy/Contact)
- Ausführung:
  ```bash
  make ui-regression
  ```

## CI-Abdeckung

CI führt bei **PR/Push** und **Nightly** aus:

- Smoke
- Regression

Die Artefakte werden immer als GitHub Actions Artifact hochgeladen (`artifacts/`).
