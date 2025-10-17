# Руководство по запуску сервисов

## Быстрый старт

### 1. Подготовка окружения

```bash
# Установить зависимости
pip install -r requirements.txt

# Активировать виртуальное окружение (если нужно)
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Установка .env файла

```bash
# Скопировать и заполнить переменные окружения
cp .env.example .env
```

**Обязательные переменные:**
```
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
OPENROUTER_API_KEY=YOUR_API_KEY
```

### 3. Запуск сервисов

#### Frontend (React + Next.js)
```bash
cd frontend/web
npm install
npm run dev
# Доступен на http://localhost:3000
```

#### Backend API (FastAPI)
```bash
python -m uvicorn src.api.main:app --reload --port 8000
# Доступен на http://localhost:8000/docs
```

#### Telegram Bot (Polling)
```bash
python src/bot.py
# Бот будет слушать сообщения из Telegram
```

---

## Возможные проблемы

### 💥 Ошибка 429 - Rate Limit Exceeded

**Сообщение ошибки:**
```
Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day'}}
```

**Причины:**
- Превышен суточный лимит бесплатных запросов на OpenRouter
- Лимит сбрасывается в 00:00 UTC
- Требуется оплата для большего количества запросов

**Решение:**
1. **Добавить кредиты**: https://openrouter.ai/account/billing/overview
2. **Дождаться следующего дня** (лимит сбросится в 00:00 UTC)
3. **Использовать более простые запросы** (меньше обработки)

**Подробнее**: См. [RATE_LIMIT_FIX_REPORT.md](./RATE_LIMIT_FIX_REPORT.md)

### 🔗 Ошибка подключения к боту

```
Error: TelegramNetworkError
```

**Решение:**
- Проверить TELEGRAM_BOT_TOKEN в .env
- Убедиться в наличии интернета
- Проверить, что Token еще валиден

### 🗄️ Ошибка базы данных

```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Решение:**
```bash
# Пересоздать БД
rm data/messages.db
python -m alembic upgrade head
```

---

## Структура проекта

```
.
├── frontend/          # React приложение
│   └── web/          # Next.js приложение
├── src/              # Backend (Python)
│   ├── api/          # FastAPI
│   ├── bot.py        # Telegram бот
│   ├── llm_client.py # OpenRouter клиент
│   └── database.py   # БД управление
├── tests/            # Тесты
└── data/
    └── messages.db   # SQLite база данных
```

---

## Полезные команды

```bash
# Запустить тесты
pytest tests/ -v

# Запустить конкретный тест
pytest tests/test_bot.py::test_something -v

# Создать новую миграцию БД
alembic revision --autogenerate -m "description"

# Применить миграции БД
alembic upgrade head

# Откатить на одну версию назад
alembic downgrade -1

# Просмотреть содержимое БД
python show_table.py
```

---

## Логирование

Логи сохраняются в:
- **Bot**: `logs/bot.log`
- **Tests**: `test_logs/test.log`

Уровень логирования устанавливается в `.env`:
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Производство (Production)

Для запуска в production:

```bash
# Запустить API с Gunicorn
gunicorn src.api.main:app -w 4 -b 0.0.0.0:8000

# Запустить бот в фоне (используя systemd, supervisord или tmux)
```

---

## Документация

- [RATE_LIMIT_FIX_REPORT.md](./RATE_LIMIT_FIX_REPORT.md) - Решение ошибки 429
- [docs/ARCHITECTURE_S5.md](./docs/ARCHITECTURE_S5.md) - Архитектура системы
- [docs/guides/DEVELOPMENT.md](./docs/guides/DEVELOPMENT.md) - Гайд разработчика
- [README.md](./README.md) - Основная информация
