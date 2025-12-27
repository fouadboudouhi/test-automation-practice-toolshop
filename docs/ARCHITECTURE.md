# Architektur (Test-Automation Toolshop)

Dieses Repository enthält **Automatisierungstests** (API + UI) für die Toolshop-Demo-Anwendung.
Die Anwendung selbst läuft als Docker-Stack; die Tests laufen lokal (dein Rechner) oder in GitHub Actions (CI).

## Komponenten

### Docker-Stack (AUT)
Der Stack wird über `docker/docker-compose.yml` gestartet und besteht typischerweise aus:

- **mariadb** – Datenbank
- **laravel-api** – Backend/API (PHP/Laravel)
- **web (nginx)** – Reverse Proxy (u. a. für die API-Doku)
- **angular-ui** – Frontend/UI

> Wichtige URLs (lokal, Standardports):
- UI: `http://localhost:4200`
- API Docs: `http://localhost:8091/api/documentation`

### Test-Code

#### API-Tests (pytest)
- Pfad: `tests/api/`
- Framework: **pytest**
- Marker:
  - `smoke` – schneller Kerncheck
  - `regression` – breiterer Umfang

#### UI-Tests (Robot Framework + Browser)
- Pfad: `tests/ui/`
- Framework: **Robot Framework**
- Browser-Automation: **Robot Framework Browser** (Playwright)
- Tags:
  - `smoke`
  - `regression`

Gemeinsame UI-Keywords/Selektoren liegen unter:
- `tests/ui/resources/keywords/common.robot`

## Artefakte / Reports

Testläufe schreiben nach `artifacts/`:

- API:
  - `artifacts/api/smoke/...`
  - `artifacts/api/regression/...`
- UI:
  - `artifacts/ui/smoke/run-XXX/...`
  - `artifacts/ui/regression/run-XXX/...`

Die `run-XXX`-Ordner verhindern Überschreiben bei mehreren lokalen Läufen.

## Konfiguration per Environment

Typische Variablen (lokal & CI identisch):

- `BASE_URL` (UI) – z. B. `http://localhost:4200`
- `API_DOCS_URL` / `API_HOST` (API) – z. B. `http://localhost:8091`
- `HEADLESS` – `true|false` für UI-Tests
- `DEMO_EMAIL`, `DEMO_PASSWORD` – Login für UI-Tests

## Einstieg

Alles Wichtige ist über das Makefile gekapselt:

```bash
make test-all
```

Das macht: **up → seed → smoke → regression**.
