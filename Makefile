.PHONY: install run lint format type-check test test-unit test-integration ci clean help
.PHONY: migrate-create migrate-up migrate-down migrate-history
.PHONY: docker-build docker-up docker-down docker-logs docker-restart
.PHONY: api-run api-test api-docs
.PHONY: frontend-install frontend-dev frontend-build frontend-lint frontend-type-check

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install dependencies using uv"
	@echo "  make run             - Run the bot locally"
	@echo "  make lint            - Check code with ruff"
	@echo "  make format          - Format code with ruff"
	@echo "  make type-check      - Check types with mypy"
	@echo "  make test            - Run all tests with coverage (min 85%)"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make ci              - Run all CI checks (lint, format, type-check, test)"
	@echo "  make clean           - Remove cache and temporary files"
	@echo ""
	@echo "Database migrations:"
	@echo "  make migrate-create MSG='description' - Create new migration"
	@echo "  make migrate-up      - Apply all migrations"
	@echo "  make migrate-down    - Rollback last migration"
	@echo "  make migrate-history - Show migration history"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-up       - Start bot in Docker"
	@echo "  make docker-down     - Stop bot in Docker"
	@echo "  make docker-logs     - Show Docker logs"
	@echo "  make docker-restart  - Restart bot in Docker"
	@echo ""
	@echo "API Server:"
	@echo "  make api-run         - Run stats API server (port 8000)"
	@echo "  make api-test        - Test API endpoints with curl"
	@echo "  make api-docs        - Show API documentation URLs"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install     - Install frontend dependencies"
	@echo "  make frontend-dev         - Run frontend dev server (port 3000)"
	@echo "  make frontend-build       - Build frontend for production"
	@echo "  make frontend-lint        - Run ESLint on frontend code"
	@echo "  make frontend-type-check  - Run TypeScript type check"

install:
	uv sync --all-extras

run:
	uv run python src/main.py

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

type-check:
	uv run mypy -p src --config-file pyproject.toml

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=85

test-unit:
	uv run pytest tests/ -v -m "not integration" --cov=src --cov-report=term-missing

test-integration:
	uv run pytest tests/ -v -m integration

ci: lint format type-check test
	@echo "✅ All CI checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Database migrations
migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migrate-create MSG='description'"; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-up:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-history:
	uv run alembic history

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

docker-restart:
	docker-compose restart bot

# Database inspection commands
db-show:
	uv run python show_table.py

db-stats:
	@uv run python -c "import sqlite3; conn = sqlite3.connect('data/messages.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM messages'); total = cursor.fetchone()[0]; cursor.execute('SELECT COUNT(*) FROM messages WHERE is_deleted = 0'); active = cursor.fetchone()[0]; print(f'\n📊 Database Statistics:\n  Total messages: {total}\n  Active messages: {active}\n  Deleted messages: {total - active}\n'); conn.close()"

db-restore:
	uv run python restore_messages.py

# API Server commands
api-run:
	uv run python src/api_server.py

api-test:
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/ | python -m json.tool
	@echo "\n"
	@curl -s "http://localhost:8000/stats?period=week" | python -m json.tool

api-docs:
	@echo "API Documentation available at:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"

# ============================================================================
# Frontend команды
# ============================================================================

frontend-install:
	@echo "📦 Installing frontend dependencies..."
	cd frontend/web && pnpm install

frontend-dev:
	@echo "🚀 Starting frontend dev server..."
	cd frontend/web && pnpm dev

frontend-build:
	@echo "🏗️  Building frontend for production..."
	cd frontend/web && pnpm build

frontend-lint:
	@echo "🔍 Running ESLint..."
	cd frontend/web && pnpm lint

frontend-type-check:
	@echo "🔍 Running TypeScript type check..."
	cd frontend/web && pnpm tsc --noEmit
