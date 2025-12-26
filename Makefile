SHELL := /bin/bash

# ----------------------------
# Config (override via env)
# ----------------------------
COMPOSE_FILE ?= docker/docker-compose.yml
# Optional second compose file, e.g. docker/docker-compose.ci.yml
COMPOSE_OVERRIDE ?=

COMPOSE_PROJECT_NAME ?= toolshop-e2e

API_SERVICE  ?= laravel-api
DB_SERVICE   ?= mariadb

# Web reverse proxy (API docs live behind this)
WEB_PORT     ?= 8091
API_HOST     ?= http://localhost:$(WEB_PORT)
API_DOCS_URL ?= $(API_HOST)/api/documentation
# Backwards compatible alias (deprecated)
API_DOC_URL  ?= $(API_DOCS_URL)


# UI
UI_PORT      ?= 4200
BASE_URL     ?= http://localhost:$(UI_PORT)

SEED_CMD     ?= php artisan migrate:fresh --seed

# Robot
TEST_ROOT    ?= tests/ui
SMOKE_TAG    ?= smoke
REG_TAG      ?= regression
HEADLESS     ?= true

# Artifacts
ARTIFACTS    ?= artifacts
UI_ARTIFACTS ?= $(ARTIFACTS)/ui
API_ARTIFACTS?= $(ARTIFACTS)/api

# Pytest
API_TEST_ROOT ?= tests/api
# Compose command (supports optional override file)
COMPOSE_FILES := -f $(COMPOSE_FILE)
ifneq ($(strip $(COMPOSE_OVERRIDE)),)
COMPOSE_FILES += -f $(COMPOSE_OVERRIDE)
endif

DC := docker compose -p $(COMPOSE_PROJECT_NAME) $(COMPOSE_FILES)

.PHONY: help up down clean ps logs \
        wait-api wait-ui wait-db seed verify-seed \
        rfbrowser-init ui-smoke ui-regression \
        smoke regression test-all

help:
	@echo "Targets:"
	@echo "  make up            - start docker stack"
	@echo "  make down          - stop stack (keep volumes)"
	@echo "  make clean         - stop stack and remove volumes"
	@echo "  make seed          - wait db + migrate:fresh --seed + verify"
	@echo "  make smoke         - run SMOKE (API + UI) if available"
	@echo "  make regression    - run REGRESSION (API + UI) if available"
	@echo "  make ui-smoke      - run Robot UI smoke only"
	@echo "  make ui-regression - run Robot UI regression only"
	@echo "  make test-all      - up -> seed -> smoke -> regression"
	@echo ""
	@echo "Useful overrides:"
	@echo "  COMPOSE_PROJECT_NAME=toolshop-e2e-2 WEB_PORT=8092 UI_PORT=4201 make up"
	@echo "  HEADLESS=false make ui-smoke"

up:
	$(DC) up -d --pull missing
	$(DC) ps
	@echo "Web/API docs: $(API_DOCS_URL)"
	@echo "UI:          $(BASE_URL)"

down:
	$(DC) down

clean:
	$(DC) down -v --remove-orphans

ps:
	$(DC) ps

logs:
	$(DC) logs --no-color --tail=200

wait-api:
	@echo "Waiting for API $(API_DOCS_URL) ..."
	@for i in {1..180}; do \
		curl -fsS "$(API_DOCS_URL)" >/dev/null 2>&1 && echo "API reachable" && exit 0; \
		sleep 2; \
	done; \
	echo "API not reachable"; \
	$(DC) logs --no-color --tail=300; \
	exit 1

wait-ui:
	@echo "Waiting for UI $(BASE_URL) ..."
	@for i in {1..180}; do \
		curl -fsS "$(BASE_URL)" >/dev/null 2>&1 && echo "UI reachable" && exit 0; \
		sleep 2; \
	done; \
	echo "UI not reachable"; \
	$(DC) logs --no-color --tail=300; \
	exit 1

wait-db:
	@echo "Waiting for DB $(DB_SERVICE) ..."
	@for i in {1..120}; do \
		$(DC) exec -T $(DB_SERVICE) sh -lc 'mysqladmin ping -h 127.0.0.1 -uroot -p"$$MYSQL_ROOT_PASSWORD" --silent' >/dev/null 2>&1 && echo "DB ready" && exit 0; \
		sleep 2; \
	done; \
	echo "DB not ready"; \
	$(DC) logs --no-color --tail=300; \
	exit 1

seed: wait-api wait-db
	@echo "Running seed: $(SEED_CMD)"
	$(DC) exec -T $(API_SERVICE) $(SEED_CMD)
	$(MAKE) verify-seed

verify-seed:
	@echo "Verifying product count > 0 ..."
	@OUT="$$( $(DC) exec -T $(API_SERVICE) php artisan tinker --execute='echo \App\Models\Product::count();' 2>/dev/null || true )"; \
	COUNT="$$(echo "$$OUT" | tr -dc '0-9')"; \
	echo "Product count: $$COUNT"; \
	if [[ -z "$$COUNT" || "$$COUNT" -le 0 ]]; then \
		echo "Seed verification failed."; \
		echo "$$OUT"; \
		exit 1; \
	fi

rfbrowser-init:
	rfbrowser init

ui-smoke: rfbrowser-init wait-ui
	@mkdir -p "$(UI_ARTIFACTS)/smoke"
	BASE_URL="$(BASE_URL)" HEADLESS="$(HEADLESS)" \
	robot --outputdir "$(UI_ARTIFACTS)/smoke" --include "$(SMOKE_TAG)" "$(TEST_ROOT)"

ui-regression: rfbrowser-init wait-ui
	@mkdir -p "$(UI_ARTIFACTS)/regression"
	BASE_URL="$(BASE_URL)" HEADLESS="$(HEADLESS)" \
	robot --outputdir "$(UI_ARTIFACTS)/regression" --include "$(REG_TAG)" "$(TEST_ROOT)"

# API targets
api-smoke: wait-api
	@mkdir -p "$(API_ARTIFACTS)/smoke"
	API_HOST="$(API_HOST)" API_DOCS_URL="$(API_DOCS_URL)" \
	pytest -q -m "smoke" --junitxml="$(API_ARTIFACTS)/smoke/junit.xml" "$(API_TEST_ROOT)"

api-regression: wait-api
	@mkdir -p "$(API_ARTIFACTS)/regression"
	API_HOST="$(API_HOST)" API_DOCS_URL="$(API_DOCS_URL)" \
	pytest -q -m "regression" --junitxml="$(API_ARTIFACTS)/regression/junit.xml" "$(API_TEST_ROOT)"

# Combined entry points
smoke: api-smoke ui-smoke
regression: api-regression ui-regression

test-all: up seed smoke regression
