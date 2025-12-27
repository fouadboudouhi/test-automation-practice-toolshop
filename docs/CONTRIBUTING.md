# Contributing

## Voraussetzungen

- Docker Desktop (oder Docker Engine + Compose)
- Python (empfohlen: 3.11+)
- Node ist **nicht** nötig (UI kommt als Container)
- Robot Framework + Browser Library (kommt über `requirements.txt`)

## Setup (lokal)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
rfbrowser init
```

## Tests ausführen

Alles über das Makefile:

```bash
make test-all
```

Oder separat:

```bash
make smoke
make regression
make api-smoke
make ui-smoke
```

Tipps:
- UI sichtbar ausführen:
  ```bash
  HEADLESS=false make ui-smoke
  ```

## Code-Qualität (manuell)

Wir nutzen keine lokalen Git-Hooks (pre-commit) als Pflicht.
Wenn du vor einem PR lokal prüfen willst:

```bash
ruff check .
ruff format .
```

## Artefakte

Nach jedem Lauf findest du Logs/Reports unter `artifacts/`.
Diese Ordner werden **nicht** committet.
