.PHONY: setup dev build edge logs db shell tests migrate backend-shell

# =============================================================================
# SETUP
# =============================================================================
setup:
	cd backend && pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install

setup-all: setup setup-frontend

# =============================================================================
# DEVELOPMENT
# =============================================================================
dev:
	cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# =============================================================================
# DOCKER COMPOSE
# =============================================================================
docker-up:
	docker compose up -d

docker-up-prod:
	docker compose -f docker-compose.prod.yml up -d

docker-down:
	docker compose down

docker-down-prod:
	docker compose -f docker-compose.prod.yml down

docker-rebuild:
	docker compose down -v
	docker compose up --build -d

docker-rebuild-prod:
	docker compose -f docker-compose.prod.yml down -v
	docker compose -f docker-compose.prod.yml up --build -d

# =============================================================================
# LOGS
# =============================================================================
logs:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

logs-all:
	docker compose logs -f

# =============================================================================
# ALEMBIC MIGRATIONS
# =============================================================================
# Create a new migration (requires message)
# Usage: make migration msg="Add user table"
migration:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# Create empty migration for manual editing
# Usage: make migration-empty msg="Custom migration"
migration-empty:
	cd backend && alembic revision -m "$(msg)"

# Apply all pending migrations
migrate:
	cd backend && alembic upgrade head

# Rollback last migration
migrate-rollback:
	cd backend && alembic downgrade -1

# Show current migration version
migrate-current:
	cd backend && alembic current

# Show migration history
migrate-history:
	cd backend && alembic history --verbose

# Rollback to specific version
# Usage: make migrate-to version=abc123
migrate-to:
	cd backend && alembic downgrade $(version)

# =============================================================================
# DATABASE
# =============================================================================
# Connect to PostgreSQL shell
db:
	docker exec -it aurumai-postgres-dev psql -U aurumai -d aurumai

db-prod:
	docker exec -it aurumai-postgres-prod psql -U aurumai -d aurumai

# Drop and recreate database (DESTRUCTIVE - development only)
db-reset:
	docker compose down postgres
	docker volume rm aurumai-mockup_postgres-data
	docker compose up -d postgres
	sleep 5
	$(MAKE) migrate

# =============================================================================
# SHELLS
# =============================================================================
edge:
	docker exec -it aurumai-edge-dev bash

backend-shell:
	docker exec -it aurumai-backend-dev bash

frontend-shell:
	docker exec -it aurumai-frontend-dev sh

# =============================================================================
# TESTING
# =============================================================================
tests:
	cd backend && pytest -v

test-coverage:
	cd backend && pytest --cov=. --cov-report=html --cov-report=term

test-frontend:
	cd frontend && npm test

# =============================================================================
# LINTING & FORMATTING
# =============================================================================
lint:
	cd backend && ruff check .

lint-fix:
	cd backend && ruff check . --fix

format:
	cd backend && black .

format-check:
	cd backend && black . --check

mypy:
	cd backend && mypy .

lint-all: lint format-check mypy

# =============================================================================
# UTILITIES
# =============================================================================
tree:
	tree -L 3 .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

help:
	@echo "Available targets:"
	@echo "  setup              - Install backend dependencies"
	@echo "  setup-all          - Install all dependencies"
	@echo "  dev                - Run backend in development mode"
	@echo "  docker-up          - Start all services (development)"
	@echo "  docker-up-prod     - Start all services (production)"
	@echo "  migration          - Create new migration (requires msg=)"
	@echo "  migrate            - Apply all pending migrations"
	@echo "  migrate-rollback   - Rollback last migration"
	@echo "  db                 - Connect to PostgreSQL shell"
	@echo "  tests              - Run backend tests"
	@echo "  lint               - Run linter"
	@echo "  clean              - Remove Python cache files"

