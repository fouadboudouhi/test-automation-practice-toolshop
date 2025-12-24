# Test Automation – Practice Software Testing (Toolshop)

Dieses Repository enthält UI-Testautomatisierung mit **Robot Framework** + **robotframework-browser (Playwright)**.
Getestet wird gegen eine **lokal/CI gestartete Toolshop-Instanz via Docker Compose**, damit die Tests nicht von Cloudflare/Anti-Bot abhängig sind.

## Ziele

- **Smoke Tests** laufen schnell als **Quality Gate** bei jedem Push/PR.
- **Regression Tests** laufen **nur wenn Smoke grün ist** und machen den Workflow **rot**, wenn ein echter Bug in der App existiert.
- **Deterministische Testdaten**: vor jedem Lauf wird die DB per **migrate:fresh --seed** neu aufgebaut.
- **Saubere Artefakte**: Robot `output.xml`, `log.html`, `report.html` + Screenshots als CI-Artifacts.

---

## Architektur

```
┌────────────────────────────┐
│ Robot Framework (Browser)  │
│  - headless in CI          │
│  - headed lokal (optional) │
└───────────────┬────────────┘
                │  BASE_URL (UI)
                ▼
        ┌─────────────────┐
        │ Angular UI      │  http://localhost:4200
        └────────┬────────┘
                 │ API Calls
                 ▼
        ┌──────────────────┐
        │ nginx (web)      │  http://localhost:8091
        │  - HTTP Endpunkt │  /api/documentation
        │  - fastcgi -> FPM│
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ laravel-api (FPM)│  intern: :9000
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ mariadb          │
        └──────────────────┘
```

**Warum nginx?**  
Das `laravel-api` Image ist in der Praxis ein **PHP-FPM** Container (kein HTTP). nginx stellt den **HTTP-Einstieg** bereit und leitet PHP Requests via **FastCGI** an FPM weiter. Das macht `curl`-Readiness checks und CI stabil/deterministisch.

---

## Quickstart (lokal)

Voraussetzungen:
- Docker Desktop / Docker Engine
- Python + Robot Framework Dependencies (siehe `requirements.txt`)

### 1) Stack starten
```bash
docker compose -f docker/docker-compose.yml up -d --pull missing
```

### 2) Datenbank seeden
```bash
docker compose -f docker/docker-compose.yml exec -T laravel-api php artisan migrate:fresh --seed
```

### 3) Browser (Playwright) initialisieren
```bash
rfbrowser init
```

### 4) Smoke / Regression ausführen
```bash
robot --outputdir artifacts_local/smoke --include smoke ui-tests
robot --outputdir artifacts_local/regression --include regression ui-tests
```

Oder alles in einem:
```bash
bash Scripts/run_all.sh
```

---

## Konfiguration (Environment Variablen)

Standardwerte sind in Scripts/CI bereits sinnvoll gesetzt.

- `SPRINT` (default `sprint5`) – steuert die Docker Images `testsmith/practice-software-testing-${SPRINT}-...`
- `UI_PORT` (default `4200`) – Host-Port für die Angular UI
- `API_PORT` (default `8091`) – Host-Port für nginx/API
- `BASE_URL` (default `http://localhost:${UI_PORT}`)
- `API_DOC_URL` (default `http://localhost:${API_PORT}/api/documentation`)
- `HEADLESS` (default `true` in CI) – lokal z.B. `export HEADLESS=false`
- `DEMO_EMAIL`, `DEMO_PASSWORD` – Demo Credentials (falls Tests Login nutzen)

Beispiel:
```bash
SPRINT=sprint5 API_PORT=18091 UI_PORT=4200 bash Scripts/run_all.sh
```

---

## GitHub Actions CI

Workflow: `.github/workflows/ci-ui-tests.yml`

- Startet Docker Compose
- Wartet auf DB + seeded
- **Smoke** als Quality Gate
- Nur wenn Smoke grün ist: **Regression**
- Lädt Robot Artefakte hoch (Smoke + Regression)

Hinweis: In CI wird `API_PORT=18091` genutzt, um Port-Kollisionen auf Shared Runnern zu vermeiden.

---

## Wichtige Pfade

- `docker/docker-compose.yml` – App Stack (ohne cron)
- `docker/nginx/default.conf` – nginx FastCGI Proxy Config
- `Scripts/run_all.sh` – lokal: up -> wait -> seed -> smoke -> regression (optional cleanup)
- `ui-tests/` – Robot Suites (Smoke/Regression)
- `artifacts_local/` – lokale Robot Reports
- `artifacts/` – CI Robot Reports (GitHub Artifacts)

---

## Troubleshooting

### API/UI nicht erreichbar
- `docker compose -f docker/docker-compose.yml ps`
- `docker compose -f docker/docker-compose.yml logs --no-color --tail=200`

### Seed Probleme / keine Produkte
- `docker compose -f docker/docker-compose.yml exec -T laravel-api php artisan tinker --execute="echo \App\Models\Product::count();"`

### Ports belegt
- lokal Ports ändern:
  ```bash
  API_PORT=18091 UI_PORT=4201 docker compose -f docker/docker-compose.yml up -d
  ```

---

## Lizenz / Hinweis

Dieses Repo ist ein privates Lern-/Demo-Projekt. Die App-Images stammen von der Practice Software Testing Toolshop-Umgebung.
