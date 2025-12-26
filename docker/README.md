# Docker: Practice Software Testing (local stack)

This repo runs UI tests **against a locally hosted Toolshop stack** to avoid Cloudflare/bot-protection flakiness.

## Start

From repo root:

```bash
docker compose -f docker/docker-compose.yml up -d --pull missing
```

Default URLs:
- UI: http://localhost:4200
- API (nginx proxy): http://localhost:8091 (e.g. `/api/documentation`)

### Optional overrides

You can override ports and sprint at runtime:

```bash
SPRINT=sprint5 API_PORT=18091 UI_PORT=4200 docker compose -f docker/docker-compose.yml up -d
```

## Stop

```bash
docker compose -f docker/docker-compose.yml down -v
```
