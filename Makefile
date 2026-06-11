.PHONY: build up down migrate seed shell test start

# Build the docker images
build:
	docker compose build

# Start services (postgres, redis, migrate, api, worker)
up:
	docker compose up --build -d

# Stop and remove containers
down:
	docker compose down

# Run alembic migrations (runs inside a temporary container)
migrate:
	docker compose run --rm -e ENVIRONMENT=development migrate

# Seed data (run inside api container)
seed:
	docker compose run --rm api python scripts/seed.py --admin-email $(ADMIN_EMAIL) --admin-password $(ADMIN_PASSWORD)

# Open a shell inside api container
shell:
	docker compose run --rm api /bin/bash

# Run tests locally using venv
test:
	python -m pytest -q

# Start uvicorn locally (dev without docker)
start:
	uvicorn app.main:app --reload
