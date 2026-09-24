# Only Broker – developer commands (run from broker-only/)
COMPOSE = docker compose -f infra/compose/docker-compose.dev.yml
PY = backend/.venv/bin/python
MANAGE = cd backend && DJANGO_DEBUG=true .venv/bin/python manage.py

.PHONY: help env up down logs seed test lint fmt shell phone local-setup local-run local-worker local-seed local-test

help:  ## Show commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

env:  ## Create backend/.env with fresh random keys (once)
	@test -f backend/.env || (cp backend/.env.example backend/.env && \
	  python3 -c "import os,base64,secrets;p='backend/.env';s=open(p).read();s=s.replace('DJANGO_SECRET_KEY=change-me','DJANGO_SECRET_KEY='+secrets.token_urlsafe(48)).replace('OB_FIELD_KEY=','OB_FIELD_KEY='+base64.b64encode(os.urandom(32)).decode()).replace('OB_PHONE_PEPPER=','OB_PHONE_PEPPER='+secrets.token_urlsafe(32));open(p,'w').write(s)" && \
	  echo "backend/.env created")

# --- Docker (recommended) -------------------------------------------------------
up: env  ## Start db, redis, api (:8000, HTTP+WebSocket), worker, beat
	$(COMPOSE) up -d --build
	@echo "API: http://localhost:8000/v1/docs   Admin: http://localhost:8000/django-admin/"

phone:  ## Print the address to type into the phone app (Settings → server), same Wi-Fi
	@IP=$$( (ipconfig getifaddr en0 || ipconfig getifaddr en1 || hostname -I | awk '{print $$1}') 2>/dev/null | head -1 ); \
	  echo "In the app: Settings → Live server → http://$$IP:8000"; \
	  echo "Check from the phone's browser first: http://$$IP:8000/health should say {\"ok\": true}"

down:  ## Stop everything (data is kept)
	$(COMPOSE) down

logs:  ## Follow logs
	$(COMPOSE) logs -f api worker

seed:  ## Load Thane West master data + demo brokers/listings
	$(COMPOSE) exec api python manage.py seed_thane_west --demo

test:  ## Run the test suite in Docker
	$(COMPOSE) exec api pytest

shell:  ## Django shell
	$(COMPOSE) exec api python manage.py shell

# --- Without Docker ----------------------------------------------------------------
local-setup: env  ## venv + deps + database (needs Postgres 16 + PostGIS + GDAL + Redis installed)
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
	./scripts/dev_db_setup.sh
	$(MANAGE) migrate

local-run:  ## API + WebSocket on :8000 (LAN-visible for phones)
	$(MANAGE) runserver 0.0.0.0:8000

local-worker:  ## Celery worker + beat in one process (dev only)
	cd backend && .venv/bin/celery -A config worker -B -l info

local-seed:  ## Seed Thane West + demo data
	$(MANAGE) seed_thane_west --demo

local-test:  ## Run tests
	cd backend && .venv/bin/pytest

lint:  ## Lint + format check
	cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .

fmt:  ## Auto-format
	cd backend && .venv/bin/ruff format . && .venv/bin/ruff check --fix .
