# CI (GitHub Actions)

Die CI ist bewusst „lean“ gehalten und nutzt das **Makefile** als Single Source of Truth.

## Workflow

- Datei: `.github/workflows/ci-ui-tests.yml`
- Trigger:
  - **Push** auf `main`
  - **Pull Request** gegen `main`
  - **Nightly** (geplanter Lauf)

## Was passiert im CI-Lauf?

1. **Checkout** des Repos
2. **Docker-Stack starten** (Compose)
3. **Warten**, bis API & DB bereit sind
4. **DB migrieren + seeden** (`php artisan migrate:fresh --seed`)
5. **Smoke-Tests ausführen**
   - API Smoke (pytest)
   - UI Smoke (Robot)
6. **Regression-Tests ausführen**
   - API Regression (pytest)
   - UI Regression (Robot)
7. **Artefakte uploaden** (`artifacts/`)

> In CI werden die Artefakte immer hochgeladen, auch wenn Tests fehlschlagen (hilft bei Debugging).

## Warum Makefile in der CI?

- Gleiche Kommandos lokal wie in CI → weniger „works on my machine“
- Weniger duplizierte Logik in YAML
- Einfache Erweiterbarkeit (z. B. neue Targets)

## Nightly

Nightly läuft denselben Smoke+Regression-Flow wie PR/Push.
Damit findest du „flaky“ Probleme oder externe Änderungen (z. B. Image-Updates) ohne dass jemand pushen muss.
