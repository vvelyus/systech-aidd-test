.PHONY: install run lint format type-check test ci clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make run        - Run the bot"
	@echo "  make lint       - Check code with ruff"
	@echo "  make format     - Format code with ruff"
	@echo "  make type-check - Check types with mypy"
	@echo "  make test       - Run tests with pytest"
	@echo "  make ci         - Run all CI checks (lint, format, type-check, test)"
	@echo "  make clean      - Remove cache and temporary files"

install:
	uv sync --all-extras

run:
	uv run python src/main.py

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

type-check:
	uv run mypy src/

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

ci: lint format type-check test
	@echo "✅ All CI checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

