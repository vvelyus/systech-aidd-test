<!-- f93d9498-8b72-424c-ac96-ce7241702aa9 8f6b9336-79ff-4791-9f04-0e5b546e4f2a -->
# План: Спринт D0 - Basic Docker Setup

## Обзор

Контейнеризация всех сервисов проекта для запуска через `docker-compose up`. MVP подход с фокусом на простоту и скорость. Используем SQLite для упрощения развертывания.

## Архитектура

```
Docker Network
├── bot (Python + UV)         - Telegram бот
├── api (Python + UV)         - FastAPI статистика  
├── frontend (Next.js + pnpm) - Веб-интерфейс
└── SQLite файл в volume      - База данных
```

## Критерии готовности

- [ ] Команда `docker-compose up` запускает все 3 сервиса
- [ ] Bot успешно подключается к SQLite
- [ ] API доступен на http://localhost:8000
- [ ] Frontend доступен на http://localhost:3000
- [ ] Frontend успешно подключается к API
- [ ] Миграции базы данных применяются автоматически
- [ ] README.md содержит инструкции по Docker запуску
- [ ] devops-roadmap.md обновлен со ссылкой на план

## Этапы реализации

### 1. Создание .dockerignore файлов

Создать `.dockerignore` для оптимизации сборки образов (исключить ненужные файлы).

**Файлы:**

- `devops/.dockerignore.bot`
- `devops/.dockerignore.api`  
- `devops/.dockerignore.frontend`

**Исключения (общие):**

```
# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Node.js
node_modules/
.next/

# Git и env
.git/
.gitignore
.env
*.env.local

# Logs и данные
*.log
logs/
test_logs/
data/

# IDE
.vscode/
.idea/
.cursor/

# Тесты и документация
tests/
docs/
*.md
```

### 2. Dockerfile для Bot (простой single-stage)

Создать `devops/Dockerfile.bot` - простой образ без multi-stage.

**Содержимое:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка UV
RUN pip install --no-cache-dir uv

# Копирование зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --no-dev

# Копирование исходников
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Создание директорий
RUN mkdir -p data logs

# Применение миграций и запуск
CMD uv run alembic upgrade head && uv run python src/main.py
```

**Ключевые моменты:**

- Single-stage (без оптимизаций)
- Миграции запускаются в CMD перед запуском бота
- Простота > оптимизация

### 3. Dockerfile для API (простой single-stage)

Создать `devops/Dockerfile.api` - аналогичен Bot, но запускает API сервер.

**Содержимое:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка UV
RUN pip install --no-cache-dir uv

# Копирование зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --no-dev

# Копирование исходников
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Создание директорий
RUN mkdir -p data logs

# Открываем порт
EXPOSE 8000

# Применение миграций и запуск API
CMD uv run alembic upgrade head && uv run python src/api_server.py
```

**Отличия от Bot:**

- EXPOSE 8000
- Запускает `api_server.py` вместо `main.py`
- Не нужны prompts/

### 4. Dockerfile для Frontend (простой single-stage)

Создать `devops/Dockerfile.frontend` - Next.js с pnpm.

**Содержимое:**

```dockerfile
FROM node:20-slim

WORKDIR /app

# Установка pnpm
RUN npm install -g pnpm

# Копирование зависимостей
COPY package.json pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install --frozen-lockfile

# Копирование исходников
COPY . .

# Открываем порт
EXPOSE 3000

# Запуск в dev режиме (MVP)
CMD ["pnpm", "dev"]
```

**Ключевые моменты:**

- Development режим (`pnpm dev`) для MVP
- Без production build (упростим для начала)
- Single-stage

### 5. Создание docker-compose.yml

Создать `docker-compose.yml` для всех 3 сервисов.

**Содержимое:**

```yaml
version: '3.8'

services:
  bot:
    build:
      context: .
      dockerfile: devops/Dockerfile.bot
      dockerignore: devops/.dockerignore.bot
    container_name: systech-aidd-bot
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./prompts:/app/prompts:ro
    restart: unless-stopped
    networks:
      - systech-network

  api:
    build:
      context: .
      dockerfile: devops/Dockerfile.api
      dockerignore: devops/.dockerignore.api
    container_name: systech-aidd-api
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - systech-network

  frontend:
    build:
      context: ./frontend/web
      dockerfile: ../../devops/Dockerfile.frontend
      dockerignore: ../../devops/.dockerignore.frontend
    container_name: systech-aidd-frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - systech-network

networks:
  systech-network:
    driver: bridge
```

**Важно:**

- Все сервисы используют общий volume `./data` для SQLite
- Проброс портов 8000 и 3000 для доступа снаружи
- Bot и API запускают миграции при старте (в CMD)
- Общая сеть для взаимодействия

### 6. Создание .env.example

Создать шаблон `.env.example` с описанием всех переменных.

**Содержимое:**

```ini
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Database Configuration (SQLite)
DATABASE_URL=sqlite+aiosqlite:///data/messages.db

# Logging Configuration
LOG_LEVEL=INFO
```

**Примечание:** DATABASE_URL указывает на файл в shared volume `/data/`.

### 7. Локальное тестирование

Протестировать запуск всех сервисов.

**Шаги:**

1. Создать `.env` на основе `.env.example`
2. Запустить: `docker-compose build`
3. Запустить: `docker-compose up`
4. Проверить логи каждого сервиса
5. Проверить API: `curl http://localhost:8000/health`
6. Открыть Frontend: `http://localhost:3000`
7. Проверить работу Bot в Telegram

**Чек-лист:**

- [ ] Сборка всех образов проходит без ошибок
- [ ] `docker-compose up` запускается без ошибок
- [ ] Миграции применены успешно (проверить логи)
- [ ] SQLite файл создан в `./data/messages.db`
- [ ] Bot запущен и отвечает в Telegram
- [ ] API отвечает на http://localhost:8000/health
- [ ] Frontend доступен на http://localhost:3000
- [ ] Frontend успешно получает данные от API
- [ ] Логи записываются в `./logs/`

**Команды для проверки:**

```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка логов
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend

# Проверка API
curl http://localhost:8000/health

# Остановка
docker-compose down

# Полная пересборка
docker-compose build --no-cache
docker-compose up
```

### 8. Обновление README.md

Добавить раздел "🐳 Docker Setup" в основной README.md (после раздела "Быстрый старт").

**Содержание раздела:**

````markdown
## 🐳 Docker Setup

### Требования

- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose v2.0+

### Запуск через Docker

1. **Настройка переменных окружения**

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
````

Отредактируйте `.env` и укажите ваши токены.

2. **Запуск всех сервисов**
```bash
docker-compose up
```


Или в фоновом режиме:

```bash
docker-compose up -d
```

3. **Проверка работы**

- Bot: проверьте в Telegram
- API: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Команды управления

```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend

# Остановка всех сервисов
docker-compose down

# Пересборка образов
docker-compose build

# Пересборка без кеша
docker-compose build --no-cache

# Просмотр статуса
docker-compose ps
```

### Troubleshooting

**Проблема:** Порты 8000 или 3000 уже заняты

Решение: Измените порты в `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # API
  - "3001:3000"  # Frontend
```

**Проблема:** Ошибка подключения к БД

Решение: Проверьте, что директория `./data` существует и имеет права на запись.

**Проблема:** Frontend не подключается к API

Решение: Проверьте переменную `NEXT_PUBLIC_API_URL` в docker-compose.yml.

**Проблема:** Миграции не применились

Решение: Проверьте логи и запустите миграции вручную:

```bash
docker-compose exec bot uv run alembic upgrade head
```



````

### 9. Обновление devops-roadmap.md

Обновить статус спринта D0 и добавить ссылку на план.

**Изменения:**

В таблице спринтов:

```markdown
| Код | Описание | Статус | План |
|-----|----------|--------|------|
| D0 | Basic Docker Setup | ✅ Completed | [план](plans/sprint-d0-plan.md) |
````

В секции "Спринт D0":

```markdown
## Спринт D0: Basic Docker Setup

**Статус:** ✅ Completed  
**План:** [devops/doc/plans/sprint-d0-plan.md](plans/sprint-d0-plan.md)

### Цели
...
```

### 10. Создание отчета о завершении

Создать `devops/doc/plans/sprint-d0-plan.md` - копия этого плана.

Создать `devops/doc/sprint-d0-completion.md` с кратким отчетом.

**Содержание:**

```markdown
# Спринт D0 - Отчет о завершении

**Дата завершения:** [дата]  
**Статус:** ✅ Завершен

## Реализовано

### Dockerfiles (Single-stage, MVP)
- `devops/Dockerfile.bot` - Python + UV для Telegram бота
- `devops/Dockerfile.api` - Python + UV для FastAPI
- `devops/Dockerfile.frontend` - Node.js + pnpm для Next.js

### Docker Compose
- `docker-compose.yml` - оркестрация 3 сервисов
- Общий volume для SQLite
- Проброс портов 8000, 3000
- Автоматические миграции при старте

### Конфигурация
- `.dockerignore` файлы для оптимизации сборки
- `.env.example` с описанием переменных
- README.md обновлен с инструкциями

## Результат

✅ Команда `docker-compose up` запускает все сервисы  
✅ Bot подключается к SQLite  
✅ API доступен на http://localhost:8000  
✅ Frontend доступен на http://localhost:3000  
✅ Миграции применяются автоматически  

## Структура файлов

```

devops/

├── Dockerfile.bot

├── Dockerfile.api

├── Dockerfile.frontend

├── .dockerignore.bot

├── .dockerignore.api

├── .dockerignore.frontend

└── doc/

├── plans/

│   └── sprint-d0-plan.md

└── sprint-d0-completion.md

docker-compose.yml (создан)

.env.example (создан)

README.md (обновлен)

```

## MVP подход

- Single-stage Dockerfiles (без оптимизации)
- Development режим для Frontend
- SQLite для упрощения
- Миграции в CMD (без отдельного entrypoint)
- Фокус на "работает" > "оптимизировано"

## Следующие шаги

**Спринт D1: Build & Publish**
- GitHub Actions для автоматической сборки
- Публикация образов в GHCR
- CI/CD pipeline
```

## Структура итоговых файлов

```
devops/
├── Dockerfile.bot
├── Dockerfile.api
├── Dockerfile.frontend
├── .dockerignore.bot
├── .dockerignore.api
├── .dockerignore.frontend
└── doc/
    ├── devops-roadmap.md (обновлен)
    ├── plans/
    │   └── sprint-d0-plan.md
    └── sprint-d0-completion.md

docker-compose.yml (создан)
.env.example (создан)
README.md (обновлен с Docker инструкциями)
```

## Важные замечания

### MVP подход

- **Single-stage Dockerfiles** - без multi-stage оптимизаций
- **Development режим** - Frontend в dev режиме (`pnpm dev`)
- **SQLite** - простая файловая БД вместо PostgreSQL
- **Миграции в CMD** - без отдельного entrypoint скрипта
- **Фокус на простоту** - "работает" важнее "оптимизировано"

### SQLite в Docker

- Shared volume `./data` для всех сервисов
- Файл БД: `./data/messages.db`
- Миграции применяются Bot и API при старте
- Текущие данные можно не сохранять (чистый старт)

### Сетевое взаимодействие

- Внутри Docker: `http://api:8000`, `http://bot:8000`
- Снаружи Docker: `http://localhost:8000`, `http://localhost:3000`
- Frontend использует `localhost` (запросы из браузера)

## Риски и решения

**Риск 1:** Конфликт портов 8000/3000

- **Решение:** Документировать в troubleshooting, предложить альтернативные порты

**Риск 2:** Миграции не применяются

- **Решение:** Миграции в CMD с явной проверкой ошибок

**Риск 3:** Frontend не видит API

- **Решение:** Проверить NEXT_PUBLIC_API_URL и проброс портов

**Риск 4:** Проблемы с правами на ./data

- **Решение:** Документировать создание директории с правильными правами

## Время выполнения

Оценка: 2-3 часа

- Dockerfiles и .dockerignore: 40 мин
- docker-compose.yml: 30 мин
- .env.example: 10 мин
- Локальное тестирование: 40 мин
- Документация README.md: 30 мин
- Обновление roadmap и отчет: 20 мин

### To-dos

- [ ] Создать .dockerignore файлы для Bot, API и Frontend
- [ ] Создать devops/Dockerfile.bot (Python + UV, простой образ)
- [ ] Создать devops/Dockerfile.api (аналогичен Bot, порт 8000)
- [ ] Создать devops/Dockerfile.frontend (Node.js + pnpm)
- [ ] Создать devops/docker-entrypoint.sh для автоматических миграций
- [ ] Обновить docker-compose.yml для 4 сервисов (postgres, bot, api, frontend)
- [ ] Создать .env.example с описанием всех переменных для Docker
- [ ] Протестировать запуск всех сервисов через docker-compose up
- [ ] Обновить README.md с инструкциями по Docker запуску
- [ ] Создать devops/doc/sprint-d0-completion.md с отчетом о завершении