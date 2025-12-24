SHELL := /bin/bash

COMPOSE_FILE ?= docker/docker-compose.yml

API_SERVICE  ?= laravel-api
DB_SERVICE   ?= mariadb

BASE_URL     ?= http://localhost:4200
API_DOC_URL  ?= http://localhost:8091/api/documentation

SEED_CMD     ?= php artisan migrate:fresh --seed

TEST_ROOT    ?= ui-tests
SMOKE_TAG    ?= smoke
REG_TAG      ?= regression

ARTIFACTS    ?= artifacts_local

DC := docker compose -f $(COMPOSE_FILE)

.PHONY: help up down clean logs ps wait-api wait-db seed verify-seed rfbrowser-init smoke regression test-all

help:
	@echo "Targets:"
	@echo "  make up            - start docker stack"
	@echo "  make down          - stop stack (keep volumes)"
	@echo "  make clean         - stop stack and remove volumes"
	@echo "  make seed          - wait db + migrate:fresh --seed"
	@echo "  make smoke         - run smoke tests (tagged)"
	@echo "  make regression    - run regression tests (tagged)"
	@echo "  make test-all      - seed -> smoke (gate) -> regression"
	@echo "  make logs          - tail stack logs"
	@echo "  make ps            - show stack status"

up:
	$(DC) up -d --pull missing
	$(DC) ps

down:
	$(DC) down

clean:
	$(DC) down -v

ps:
	$(DC) ps

logs:
	$(DC) logs --no-color --tail=200

wait-api:
	@echo "Waiting for API $(API_DOC_URL) ..."
	@for i in {1..120}; do \
		curl -fsS "$(API_DOC_URL)" >/dev/null 2>&1 && echo "API reachable" && exit 0; \
		sleep 2; \
	done; \
	echo "API not reachable"; \
	$(DC) logs --no-color --tail=300; \
	exit 1

wait-db:
	@echo "Waiting for DB $(DB_SERVICE) ..."
	@for i in {1..60}; do \
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

smoke: rfbrowser-init
	BASE_URL="$(BASE_URL)" robot --outputdir "$(ARTIFACTS)/smoke" --include "$(SMOKE_TAG)" "$(TEST_ROOT)"

regression: rfbrowser-init
	BASE_URL="$(BASE_URL)" robot --outputdir "$(ARTIFACTS)/regression" --include "$(REG_TAG)" "$(TEST_ROOT)"

test-all: up seed smoke regression