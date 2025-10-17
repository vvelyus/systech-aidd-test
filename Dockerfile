# Dockerfile для Telegram бота
# Sprint S1: Docker контейнеризация приложения

# Используем официальный образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем uv для управления зависимостями
# uv - современный быстрый менеджер пакетов Python
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости проекта
# --no-dev исключает dev зависимости для production
RUN uv sync --no-dev

# Копируем исходный код приложения
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Создаем директории для данных и логов
RUN mkdir -p data logs

# Применяем миграции БД при старте контейнера
# Это гарантирует, что схема БД всегда актуальна
RUN uv run alembic upgrade head || echo "Migrations will be applied at runtime"

# Запускаем приложение
CMD ["uv", "run", "python", "src/main.py"]
