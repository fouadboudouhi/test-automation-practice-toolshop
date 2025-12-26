# Toolshop – UI/API Test-Automation (Docker + Robot + Pytest)

Dieses Repo startet die **Practice Software Testing**-Demo via **Docker Compose** und führt darauf **UI-Tests (Robot Framework + Browser/Playwright)** sowie **API-Tests (pytest + requests)** aus – lokal und in CI.

## System-Überblick (ASCII)

```text
                 ┌────────────────────────────────────────────────┐
                 │                 Developer / CI                 │
                 │  make up / seed / smoke / regression / test-all│
                 └───────────────────────────┬────────────────────┘
                                             │
                                             │  (Host network)
                                             │
                     ┌───────────────────────┴──────────────────────────┐
                     │                Docker Compose Stack              │
                     │                                                  │
                     │  ┌──────────────┐        ┌───────────────────┐   │
Robot UI Tests ─────▶│  │ angular-ui   │ 4200   │ web (nginx)       │   │◀───── Pytest API Tests
(Playwright)         │  │ (Frontend)   │◀──────▶│ :8091 → API routes│   │       (requests)
                     │  └──────────────┘        └─────────┬─────────┘   │
                     │                                     │            │
                     │                                     │ (internal) │
                     │                            ┌────────▼────────┐   │
                     │                            │ laravel-api     │   │
                     │                            │ (Backend) :9000 │   │
                     │                            └────────┬────────┘   │
                     │                                     │            │
                     │                            ┌────────▼────────┐   │
                     │                            │ mariadb         │   │
                     │                            │ DB :3306        │   │
                     │                            └─────────────────┘   │
                     └──────────────────────────────────────────────────┘
```

> **Wichtig:** `web (nginx)` stellt i.d.R. die API inkl. Swagger unter `http://localhost:8091/api/documentation` bereit.  
> `angular-ui` läuft lokal typischerweise unter `http://localhost:4200`.

---

## Voraussetzungen

- Docker + Docker Compose
- GNU Make
- Python (für lokale Tests, z. B. 3.11+ empfohlen)
- Node brauchst du **nicht** manuell: `rfbrowser init` kümmert sich um Playwright/Browser-Binaries.

---

## Quickstart (lokal)

```bash
make up
make seed
make smoke
make regression
```

Alles in einem Lauf (Stack hochfahren → seed → smoke → regression):

```bash
make test-all
```

---

## Artefakte / Reports

Nach den Runs findest du u. a.:

- Robot Framework:
  - `artifacts/ui/smoke/{log.html,report.html,output.xml}`
  - `artifacts/ui/regression/{log.html,report.html,output.xml}`
  - Screenshots typischerweise unter `artifacts/.../screenshots/`
- Pytest:
  - `artifacts/api/smoke/junit.xml`
  - `artifacts/api/regression/junit.xml`

(Die genauen Pfade hängen an der Makefile-Konfiguration – Ziel ist: **alles unter `artifacts/`**.)

---

## Häufige Make Targets

```bash
make help         # Übersicht
make up           # Docker Stack starten
make down         # Stack stoppen (Volumes behalten)
make clean        # Stack stoppen + Volumes löschen
make seed         # DB migrieren + seeden + verifizieren
make smoke        # Smoke-Tests (Tags) ausführen
make regression   # Regression-Tests (Tags) ausführen
make test-all     # up -> seed -> smoke -> regression
make logs         # Stack logs
make ps           # docker compose ps
```

---

## Konfiguration per ENV (typisch)

Diese Werte kannst du (lokal/CI) überschreiben:

- `COMPOSE_FILE` (Default: `docker/docker-compose.yml`)
- `BASE_URL` (Default: `http://localhost:4200`)
- `API_DOC_URL` (Default: `http://localhost:8091/api/documentation`)
- `HEADLESS` (`true/false`)
- `DEMO_EMAIL`, `DEMO_PASSWORD`
- `ARTIFACTS` (z. B. `artifacts`)
- Optional: Compose Project Name (gegen Port-Konflikte), z. B.  
  `COMPOSE_PROJECT_NAME=toolshop-e2e`

Beispiel:

```bash
BASE_URL=http://localhost:4200 HEADLESS=false make smoke
```

---

## Ordnerstruktur (Tests)

- `ui-tests/`
  - `smoke/` – UI Smoke Suites
  - `regression/` – UI Regression Suites
  - `resources/` – gemeinsame Keywords/Variablen
- `api-tests/`
  - `tests/smoke/`
  - `tests/regression/`

---

## Troubleshooting

### “Bind for 0.0.0.0:3306 failed: port is already allocated”
Auf deinem Host läuft bereits MySQL/MariaDB oder ein anderer Stack nutzt den Port.

Optionen:
1) Anderen Compose Project Name nutzen (parallel laufende Stacks trennen):
```bash
COMPOSE_PROJECT_NAME=toolshop-2 make up
```

2) Stack stoppen/aufräumen:
```bash
make down
make clean
docker ps
```

3) Ports im Compose via Env/Overrides anpassen (falls dein Compose das unterstützt).

### UI/Swagger ist “reachable”, aber Tests finden keine Elemente
Typisch: App ist da, aber Daten/Seed/Backend noch nicht bereit.  
Lösung: `make seed` sicherstellen und in Tests nur **gezielte Waits** verwenden (keine Sleeps).

---

## CI

Die GitHub Actions Workflow-Datei (`ci-ui-tests.yml`) führt aus:

- **Smoke** als Gate (muss grün sein)
- **Regression** nur wenn Smoke erfolgreich war
- Docker Stack wird im Job gestartet, DB wird migriert + geseedet, dann Robot Tests headless ausgeführt
- Artefakte werden als GitHub Artifacts hochgeladen

```
✅ smoke  ->  ✅ regression
❌ smoke  ->  regression wird übersprungen
```
