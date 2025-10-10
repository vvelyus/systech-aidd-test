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

# OpenRouter API (для будущих итераций)
OPENROUTER_API_KEY=your_openrouter_api_key_here
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

## Доступные команды

### Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать список команд
- `/status` - Проверить работоспособность бота

### Команды разработки

```bash
make install   # Установка зависимостей
make run       # Запуск бота
make lint      # Проверка кода линтером
make format    # Форматирование кода
make clean     # Очистка кэша и временных файлов
make help      # Показать все доступные команды
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
│   ├── config.py         # Config класс
│   └── logger.py         # Logger настройка
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

### Линтинг и форматирование

Проект использует [ruff](https://github.com/astral-sh/ruff) для линтинга и форматирования:

```bash
make lint      # Проверка кода
make format    # Автоформатирование
```

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
**Итерация 2** (⏳ В планах) - Интеграция с LLM  
**Итерация 3** (⏳ В планах) - Контекст диалога  
**Итерация 4** (⏳ В планах) - Финализация и полировка  

См. подробный план в `docs/TASKLIST.md`

## Известные ограничения

- Пока без интеграции с LLM (заглушка в ответах)
- История диалогов не сохраняется (будет в итерации 3)
- Без персистентного хранилища (in-memory для MVP)

## Лицензия

Проект создан для внутреннего использования и тестирования.

## Контакты

Для вопросов и предложений обращайтесь к команде разработки.

