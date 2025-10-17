# systech-aidd-test

AI-driven Telegram бот для тестирования интеграции с LLM через OpenRouter API.

## Описание

Простой MVP Telegram бота с поддержкой общения через различные LLM модели. Проект следует принципам KISS и создан для быстрой проверки концепции.

## Технологии

### Основной стек

- **Python 3.11+** - основной язык
- **uv** - управление зависимостями
- **aiogram 3.x** - Telegram Bot API (polling)
- **openai** - клиент для работы с LLM через OpenRouter
- **python-dotenv** - управление конфигурацией

### База данных (Sprint S1)

- **SQLite 3** - встроенная файловая БД
- **SQLAlchemy 2.0** - ORM с async поддержкой
- **aiosqlite** - асинхронный драйвер для SQLite
- **Alembic** - управление миграциями схемы БД

### Docker

- **Docker** - контейнеризация приложения
- **Docker Compose** - оркестрация контейнеров

### Инструменты качества кода

- **ruff** - линтер и форматтер (10+ категорий правил)
- **mypy** - статическая проверка типов (strict mode)
- **pytest** - тестирование с покрытием кода (target >= 85%)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd systech-aidd-test
```

### 2. Установка зависимостей

Убедитесь, что у вас установлен [uv](https://github.com/astral-sh/uv):

```bash
make install
```

или

```bash
uv sync --all-extras
```

### 3. Настройка конфигурации

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите ваши токены:

```ini
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

**Где получить токены:**
- Telegram Bot Token: [@BotFather](https://t.me/botfather) в Telegram
- OpenRouter API Key: [openrouter.ai](https://openrouter.ai/)

### 4. Инициализация базы данных

Примените миграции для создания таблиц:

```bash
make migrate-up
```

или

```bash
uv run alembic upgrade head
```

### 5. Запуск бота

#### Локально (без Docker)

```bash
make run
```

или

```bash
uv run python src/main.py
```

#### В Docker (рекомендуется для production)

```bash
# Собрать образ
make docker-build

# Запустить контейнер в фоне
make docker-up

# Просмотреть логи
make docker-logs

# Остановить контейнер
make docker-down
```

Бот запустится в режиме polling и начнет обрабатывать сообщения.

---

## 📚 Документация и гайды

### Для новых разработчиков

**🚀 Начните здесь:**
- **[docs/guides/ONBOARDING.md](docs/guides/ONBOARDING.md)** - Пошаговый онбординг за 30 минут

**📖 Основные гайды:**
- **[docs/guides/VISUAL_GUIDE.md](docs/guides/VISUAL_GUIDE.md)** - 📊 Визуализация: 10 типов диаграмм с разных точек зрения
- **[docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)** - Архитектура системы с диаграммами
- **[docs/guides/CODEBASE_TOUR.md](docs/guides/CODEBASE_TOUR.md)** - Тур по коду с примерами
- **[docs/guides/DEVELOPMENT.md](docs/guides/DEVELOPMENT.md)** - Процессы разработки и TDD
- **[docs/guides/TESTING.md](docs/guides/TESTING.md)** - Стратегия тестирования

**📂 Навигация:** [docs/guides/README.md](docs/guides/README.md) - Полный список гайдов с навигацией

### Техническая документация

- **[docs/VISION.md](docs/VISION.md)** - Полное техническое видение проекта
- **[docs/roadmap.md](docs/roadmap.md)** - Roadmap проекта и спринты
- **[docs/guides/DATABASE_SCHEMA.md](docs/guides/DATABASE_SCHEMA.md)** - Схема базы данных
- **[docs/ADR.md](docs/ADR.md)** - Architecture Decision Records

---

## Настройка VSCode/Cursor

Проект полностью настроен для работы в VSCode/Cursor. После открытия проекта:

1. **Установите рекомендуемые расширения** (`.vscode/extensions.json`):
   - Python
   - Pylance
   - Ruff
   - Even Better TOML

2. **Конфигурации запуска** (F5 или Run and Debug):
   - 🚀 Run Bot - запустить бота
   - 🐛 Debug Bot - отладка бота
   - 🧪 Run All Tests - запустить все тесты
   - 🧪 Debug Current Test File - отладка текущего файла тестов
   - 🧪 Debug Current Test Function - отладка выбранного теста
   - 🧪 Run Unit Tests Only - только юнит-тесты
   - 🧪 Run Integration Tests Only - только интеграционные тесты
   - 🧪 Run Tests with Coverage Report - тесты с HTML отчетом

3. **Задачи** (Terminal → Run Task):
   - 🔍 Lint (Ruff) - проверка кода
   - ✨ Format (Ruff) - форматирование
   - 🔎 Type Check (Mypy) - проверка типов
   - 🧪 Run Tests - запуск тестов
   - ✅ CI - Full Check - полная проверка
   - 🚀 Run Bot - запуск бота
   - 🧹 Clean Cache - очистка кэша

4. **Автоматическое форматирование** включено при сохранении файла

## Доступные команды

### Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать список команд
- `/role` - Узнать роль и функции бота
- `/status` - Проверить работоспособность бота
- `/reset` - Очистить контекст диалога

### Команды разработки

```bash
# Development
make install    # Установка зависимостей
make run        # Запуск бота локально
make lint       # Проверка кода линтером (ruff)
make format     # Форматирование кода (ruff)
make type-check # Проверка типов (mypy)
make test       # Запуск тестов с покрытием кода
make ci         # Запуск всех проверок качества
make clean      # Очистка кэша и временных файлов

# Database migrations
make migrate-create MSG='description'  # Создать новую миграцию
make migrate-up                       # Применить все миграции
make migrate-down                     # Откатить последнюю миграцию
make migrate-history                  # Показать историю миграций

# Docker
make docker-build    # Собрать Docker образ
make docker-up       # Запустить бот в Docker
make docker-down     # Остановить бот в Docker
make docker-logs     # Показать логи контейнера
make docker-restart  # Перезапустить контейнер

make help       # Показать все доступные команды
```

## Структура проекта

```
systech-aidd-test/
├── docs/                  # Документация
│   ├── ADR.md            # Architecture Decision Records
│   ├── IDEA.md           # Описание идеи
│   ├── VISION.md         # Техническое видение
│   ├── roadmap.md        # Roadmap проекта
│   ├── guides/           # Руководства
│   │   ├── DATABASE_SCHEMA.md  # Схема БД
│   │   └── ...
│   └── tasklists/        # Тасклисты спринтов
├── src/                   # Исходный код
│   ├── __init__.py
│   ├── main.py           # Точка входа
│   ├── bot.py            # TelegramBot класс
│   ├── llm_client.py     # LLMClient класс
│   ├── config.py         # Config класс
│   ├── messages.py       # Текстовые константы
│   ├── context_storage.py # Хранилище контекста (In-Memory + Database)
│   ├── database.py       # Database manager
│   ├── models.py         # SQLAlchemy модели
│   └── logger.py         # Logger настройка
├── alembic/               # Миграции БД (Alembic)
│   ├── versions/         # Файлы миграций
│   └── env.py            # Конфигурация Alembic
├── migrations/            # SQL скрипты
│   └── schema.sql        # Схема БД для ручного создания
├── prompts/               # Системные промпты (роль бота)
│   └── system_prompt.txt # Роль и поведение бота
├── tests/                 # Тесты (coverage >= 85%)
│   ├── __init__.py
│   ├── conftest.py       # Общие фикстуры
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_llm_client.py
│   ├── test_bot.py
│   ├── test_messages.py
│   ├── test_context_storage.py
│   ├── test_models.py    # Тесты моделей SQLAlchemy
│   └── test_database.py  # Тесты database manager
├── data/                  # База данных (создается автоматически)
│   └── messages.db       # SQLite БД
├── logs/                  # Логи (создается автоматически)
│   └── bot.log
├── .env.example          # Пример конфигурации
├── .env                  # Конфигурация (не в git)
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Docker Compose конфигурация
├── .dockerignore         # Исключения для Docker
├── alembic.ini           # Конфигурация Alembic
├── .gitignore
├── Makefile              # Команды управления
├── pyproject.toml        # Конфигурация uv
└── README.md
```

## Разработка

### Принципы

- **KISS** - максимальная простота решений
- **ООП** - один класс = один файл
- **Читаемость** - код должен быть самоочевидным
- **Асинхронность** - весь код использует async/await

Подробнее см. `.cursor/rules/conventions.mdc` и `docs/VISION.md`

### Контроль качества кода

Проект использует автоматизированный CI pipeline для обеспечения качества:

#### Инструменты

- **[ruff](https://github.com/astral-sh/ruff)** - линтинг и форматирование (10+ категорий правил)
- **[mypy](https://mypy.readthedocs.io/)** - статическая проверка типов (strict mode)
- **[pytest](https://pytest.org)** - тестирование с покрытием кода

#### Команды

```bash
make lint       # Проверка кода линтером (ruff)
make format     # Автоформатирование (ruff)
make type-check # Проверка типов (mypy strict mode)
make test       # Запуск тестов с покрытием кода
make ci         # Полный CI pipeline (все проверки)
```

#### CI Pipeline

Команда `make ci` выполняет все проверки качества:

1. **Lint** - проверка стиля кода (ruff)
2. **Format** - автоформатирование (ruff)
3. **Type-check** - проверка типов (mypy strict)
4. **Test** - запуск тестов с покрытием (pytest)

**Обязательно:** Все проверки CI должны проходить перед коммитом!

#### Тесты

Тестовое покрытие включает:
- Юнит-тесты для всех модулей (Config, Logger, LLMClient, TelegramBot)
- Покрытие кода >= 71% (target >= 85%)
- Асинхронные тесты с pytest-asyncio
- Проверка edge cases и обработки ошибок

## Логирование

Логи записываются в:
- `logs/bot.log` - файл с полной историей
- Консоль - для мониторинга в реальном времени

Формат лога:
```
2025-10-10 12:00:00 - systech_bot - INFO - Сообщение
```

## Текущий статус

**Sprint S0** (✅ Завершено) - MVP с in-memory storage
- Итерация 1-5: базовый функционал, LLM интеграция, контекст, AI-продукт с ролью

**Sprint S1** (🚧 В процессе) - Персистентное хранение данных
- ✅ SQLite + SQLAlchemy + Alembic
- ✅ Soft delete стратегия
- ✅ Docker контейнеризация
- ⏳ Тесты и финальная проверка

См. подробный roadmap в `docs/roadmap.md`

## Возможности

✅ **Полностью реализовано (Sprint S0 + S1):**
- 🎭 **AI-продукт с определенной ролью** - системный промпт из файла
- 🤖 Интеграция с LLM через OpenRouter API
- 🎨 Поддержка различных моделей (Claude, GPT и др.)
- 💬 Запоминание контекста диалога (последние 20 сообщений)
- 💾 **Персистентное хранение в SQLite** - история сохраняется после перезапуска
- 🗃️ **Soft delete** - данные не удаляются физически
- 🔄 Команда `/reset` для очистки контекста (мягкое удаление)
- 🎭 Команда `/role` для отображения роли и функций бота
- 📝 Гибкая настройка роли через файл `prompts/system_prompt.txt`
- ⚡ Обработка edge cases (пустые/длинные сообщения)
- 💡 Дружественные сообщения об ошибках
- 🐳 **Docker контейнеризация** - готово для production
- 🔄 **Database migrations** - Alembic для управления схемой БД
- 🧪 Юнит-тесты с покрытием кода (target >= 85%)
- 🚀 Асинхронная архитектура
- ✅ TDD подход в разработке

🎯 **Технический стек:**
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)
- SQLite + aiosqlite
- Docker + Docker Compose

## Настройка роли бота

Бот - это **AI-продукт с определенной ролью**. Роль определяется через системный промпт в файле `prompts/system_prompt.txt`.

### Как настроить роль

1. Отредактируйте файл `prompts/system_prompt.txt`:

```
Ты - [определение роли бота].

Твоя специализация: [описание специализации]

Основные функции:
- [функция 1]
- [функция 2]
- [функция 3]

Стиль общения: [описание стиля]
```

2. Перезапустите бота - новая роль будет загружена автоматически

3. Пользователи могут узнать роль бота через команду `/role`

### Преимущества

- **Гибкость:** Смена роли без изменения кода
- **Прозрачность:** Пользователь видит роль через `/role`
- **Масштабируемость:** Один код → множество специализированных ботов
- **TDD:** Полное покрытие тестами (100%)

## Лицензия

Проект создан для внутреннего использования и тестирования.

## Контакты

Для вопросов и предложений обращайтесь к команде разработки.

## 🚀 Rate Limit (429) - Решено (v2.0)

Если возникает ошибка `Error code: 429 - Rate limit exceeded: free-models-per-day`:

### ⚡ Быстрое решение

**Вариант 1** (рекомендуется): Добавить кредиты на OpenRouter
- https://openrouter.ai → Профиль → Billing
- Минимум $5-10
- Работает сразу

**Вариант 2**: Дождаться следующего дня
- Лимит сбросится в 00:00 UTC (~24 часа)

**Вариант 3**: Использовать более простые запросы
- Более короткие вопросы
- Меньше контекста
- Меньше обработки

📖 **Полная информация**: [RATE_LIMIT_FIX_REPORT.md](./RATE_LIMIT_FIX_REPORT.md)

---

## 📊 Обновления в коде (v2.0)

✅ **src/llm_client.py** - Retry удален при free-models-per-day
- Ошибка выбрасывается сразу (нет задержки)
- Retry работает для других типов лимитов
- Чистые логи без ненужных retry попыток

✅ **src/api/chat_service.py** - Дружественные сообщения
- Информативная ошибка пользователю
- Рекомендации по решению
- Быстрая обработка

### 📚 Документация
- [RATE_LIMIT_FIX_REPORT.md](./RATE_LIMIT_FIX_REPORT.md) - Полное решение
- [SERVICES_STARTUP_GUIDE.md](./SERVICES_STARTUP_GUIDE.md) - Гайд запуска
- [SESSION_COMPLETE.txt](./SESSION_COMPLETE.txt) - Техническое резюме
