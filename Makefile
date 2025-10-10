.PHONY: install run lint format clean help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies using uv"
	@echo "  make run      - Run the bot"
	@echo "  make lint     - Check code with ruff"
	@echo "  make format   - Format code with ruff"
	@echo "  make clean    - Remove cache and temporary files"

install:
	uv sync --all-extras

run:
	uv run python src/main.py

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

