# User Management – Test Automation Project

This project demonstrates a production-like test automation setup for a small User Management system.
The focus is **not feature completeness**, but **test strategy, determinism, and CI-ready architecture**.

The system is intentionally kept small to allow deep discussion of:
- test architecture
- quality gates
- reproducibility
- trade-offs

---

## System Overview

The system consists of a minimal User Management application with full test automation on API and UI level.

### Core Components
- **FastAPI** – REST API for user management
- **PostgreSQL** – persistent storage (production-like)
- **Minimal Web UI** – only for critical UI test coverage
- **pytest** – API and UI test execution
- **Playwright (Python)** – UI automation
- **Docker & Docker Compose** – reproducible environments
- **GitHub Actions** – CI pipeline
- **Allure** – test reporting and failure analysis

---

## Architecture

```
┌────────────┐      HTTP       ┌──────────────┐      SQL     ┌────────────┐
│  UI Tests  │ ─────────────▶  │   FastAPI    │ ───────────▶ │ PostgreSQL │
│ Playwright│                  │  User API    │              │            │
└────────────┘                 └──────────────┘              └────────────┘
       ▲                              ▲
       │                              │
       │            HTTP              │
       └───────── API Tests ──────────┘
                   pytest
```

---

## API Scope (intentionally limited)

### User Operations
- Create User
- Get User
- Update User
- Delete User

### Negative Cases
- Duplicate email → `409 Conflict`
- Invalid payload → `422 Unprocessable Entity`
- User not found → `404 Not Found`

---

## Test Strategy

### Test Pyramid
- **~70% API Tests** – main quality gate
- **~20% UI Tests** – critical flows only
- **~10% Smoke Tests** – availability checks

UI tests validate intent, not backend state.

---

## Deterministic Test Design

- Database reset between tests
- No test dependencies
- No uncontrolled randomness
- No static sleeps

---

## Docker & Execution Model

Services:
- `db`
- `app`

Test runners:
- `api-tests`
- `ui-tests`

Execution:
```bash
docker compose run --rm api-tests
docker compose run --rm ui-tests
```

---

## CI Pipeline

Triggers:
- Pull Requests
- Push to main

Stages:
1. Start services
2. Run API tests (hard gate)
3. Run UI tests
4. Publish Allure artifacts

---

## Allure Reporting

- Unified API + UI report
- Screenshots on UI failures
- Available locally and in CI

---

## Trade-offs

| Decision | Reason |
|--------|--------|
| PostgreSQL | Production-like |
| Few UI tests | Stability |
| No auth | Focus on testing |
| No history | Simplicity |

---

## Next Steps

- Parallel execution
- Allure history
- Contract tests
- Performance testing
