# systech-aidd-test

AI-driven Telegram бот для тестирования интеграции с LLM через OpenRouter API.

## Описание

Простой MVP Telegram бота с поддержкой общения через различные LLM модели. Проект следует принципам KISS и создан для быстрой проверки концепции.

## Технологии

- **Python 3.11+** - основной язык
- **uv** - управление зависимостями
- **aiogram 3.x** - Telegram Bot API (polling)
- **openai** - клиент для работы с LLM через OpenRouter
- **python-dotenv** - управление конфигурацией

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

### 4. Запуск бота

```bash
make run
```

или

```bash
uv run python src/main.py
```

Бот запустится в режиме polling и начнет обрабатывать сообщения.

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
- `/status` - Проверить работоспособность бота
- `/reset` - Очистить контекст диалога

### Команды разработки

```bash
make install    # Установка зависимостей
make run        # Запуск бота
make lint       # Проверка кода линтером (ruff)
make format     # Форматирование кода (ruff)
make type-check # Проверка типов (mypy)
make test       # Запуск тестов с покрытием кода
make ci         # Запуск всех проверок качества (lint + format + type-check + test)
make clean      # Очистка кэша и временных файлов
make help       # Показать все доступные команды
```

## Структура проекта

```
systech-aidd-test/
├── docs/                  # Документация
│   ├── ADR.md            # Architecture Decision Records
│   ├── IDEA.md           # Описание идеи
│   ├── VISION.md         # Техническое видение
│   └── TASKLIST.md       # План разработки
├── src/                   # Исходный код
│   ├── __init__.py
│   ├── main.py           # Точка входа
│   ├── bot.py            # TelegramBot класс
│   ├── llm_client.py     # LLMClient класс
│   ├── config.py         # Config класс
│   └── logger.py         # Logger настройка
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_llm_client.py
│   └── test_bot.py
├── logs/                  # Логи (создается автоматически)
├── .env.example          # Пример конфигурации
├── .env                  # Конфигурация (не в git)
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

**Итерация 1** (✅ Завершено) - Базовая настройка и Telegram бот
**Итерация 2** (✅ Завершено) - Интеграция с LLM через OpenRouter
**Итерация 3** (✅ Завершено) - Контекст диалога (последние 20 сообщений)
**Итерация 4** (✅ Завершено) - Финализация, тестирование и документация

См. подробный план в `docs/TASKLIST.md`

## Возможности

✅ **Полностью реализовано:**
- Интеграция с LLM через OpenRouter API
- Поддержка различных моделей (Claude, GPT и др.)
- Запоминание контекста диалога (последние 20 сообщений)
- Команда `/reset` для очистки контекста
- Обработка edge cases (пустые/длинные сообщения)
- Дружественные сообщения об ошибках
- Юнит-тесты с покрытием кода
- Асинхронная архитектура

⚠️ **Известные ограничения:**
- История диалогов хранится в памяти (сбрасывается при перезапуске)
- Нет персистентного хранилища (in-memory для MVP)
- Максимум 20 сообщений в контексте на пользователя

## Лицензия

Проект создан для внутреннего использования и тестирования.

## Контакты

Для вопросов и предложений обращайтесь к команде разработки.
