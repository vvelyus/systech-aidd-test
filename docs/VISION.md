# Техническое видение проекта

## 1. Технологии

### Core
- **Python 3.11+** - используется установленная версия
- **uv** - управление зависимостями и виртуальным окружением

### Основные библиотеки
- **aiogram 3.x** - фреймворк для Telegram Bot API (polling)
- **openai** - клиент для работы с LLM через OpenRouter
- **python-dotenv** - управление конфигурацией

### Инструменты разработки
- **make** - автоматизация команд
- **ruff** - быстрый линтер и форматтер (расширенные правила)
- **mypy** - статический анализатор типов (strict mode)
- **pytest** - фреймворк тестирования с coverage >= 85%

---

## 2. Принципы разработки

### Ключевые принципы
- **KISS** - максимальная простота решений
- **SOLID** - соблюдение принципов ООП дизайна
- **DRY** - избегание дублирования кода
- **ООП** - 1 класс = 1 файл
- **MVP-подход** - только необходимый функционал
- **Читаемость кода** превыше оптимизаций

### Качество кода
- **Type hints** - обязательны для всех публичных методов
- **Mypy strict mode** - проверка типов
- **Ruff extended rules** - расширенный набор правил линтинга
- **Test coverage >= 85%** - высокое покрытие тестами

### Правила кодирования
- Один класс в одном файле
- Docstrings (Google Style) для классов и публичных методов
- Type hints для всех публичных методов
- Понятные имена переменных и функций
- Минимальная вложенность (2-3 уровня)
- Никаких абстракций "на будущее" (но Protocol для абстракций)

### Разработка
- Тесты пишем после проверки концепции
- Все изменения проходят через `make ci`
- Рефакторинг только при сохранении функциональности

---

## 3. Структура проекта

```
systech-aidd-test/
├── docs/                       # Документация
│   ├── IDEA.md
│   ├── VISION.md
│   ├── TASKLIST.md
│   ├── TASKLIST_TECH_DEBT.md
│   └── WORKFLOW_TECH_DEBT.md
├── src/                        # Исходный код
│   ├── __init__.py
│   ├── main.py                # Точка входа
│   ├── bot.py                 # TelegramBot класс
│   ├── llm_client.py          # LLMClient класс
│   ├── config.py              # Config dataclass
│   ├── context_storage.py     # ContextStorage Protocol + реализации
│   ├── messages.py            # Текстовые константы
│   └── logger.py              # Logger настройка
├── tests/                      # Тесты (coverage >= 85%)
│   ├── __init__.py
│   ├── conftest.py            # Общие фикстуры
│   ├── integration/           # Интеграционные тесты
│   └── test_*.py              # Unit тесты
├── logs/                       # Логи
├── .cursor/rules/              # Cursor rules
│   ├── conventions.mdc
│   └── workflow.mdc
├── .env.example               # Пример конфигурации
├── .env                       # Конфигурация
├── .gitignore
├── Makefile                   # Команды управления (+ ci)
├── pyproject.toml             # Конфигурация (ruff, mypy, pytest)
├── uv.lock
└── README.md                  # Инструкция
```

---

## 4. Архитектура проекта

### Компоненты системы

1. **TelegramBot** - обработка сообщений Telegram
2. **LLMClient** - взаимодействие с OpenRouter API
3. **Config** - управление конфигурацией (immutable dataclass)
4. **ContextStorage** - абстракция хранилища контекста (Protocol)
5. **InMemoryContextStorage** - реализация in-memory хранилища
6. **Logger** - логирование событий
7. **BotMessages** - текстовые константы

### Поток данных

```
Пользователь → Telegram → TelegramBot → LLMClient → OpenRouter (LLM)
                                ↓            ↓              ↓
                                ↓      ContextStorage      ↓
                                ↓            ↓              ↓
                         Ответ пользователю ← ←  Ответ LLM
```

**Взаимодействие компонентов:**
```
1. TelegramBot получает сообщение от пользователя
2. TelegramBot вызывает LLMClient.get_response_with_context()
3. LLMClient запрашивает контекст из ContextStorage
4. LLMClient формирует запрос к OpenRouter API
5. LLMClient сохраняет ответ в ContextStorage
6. TelegramBot отправляет ответ пользователю
```

### Управление контекстом

**Архитектурный подход:**
- История диалога через абстракцию `ContextStorage` (Protocol)
- Dependency Injection в LLMClient
- Текущая реализация: `InMemoryContextStorage`
- Контекст: последние 20 сообщений на пользователя

**Преимущества архитектуры:**
- **Тестируемость:** Легко мокировать storage в тестах
- **Масштабируемость:** Замена на Redis/DB без изменений LLMClient
- **SOLID:** Следование Dependency Inversion Principle
- **Простота:** Каждый компонент решает одну задачу (SRP)

---

## 5. Модель данных

### Конфигурация (immutable dataclass)

```python
@dataclass(frozen=True)
class Config:
    telegram_token: str
    openrouter_api_key: str
    bot_name: str = "SysTech AI Assistant"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    system_prompt: str = "Ты - полезный AI-ассистент..."
    max_context_messages: int = 20
    log_file_path: str = "logs/bot.log"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Загрузка из .env с валидацией."""
        ...
```

### История диалога (in-memory dict)

```python
{
    user_id: [
        {"role": "user", "content": "сообщение пользователя"},
        {"role": "assistant", "content": "ответ бота"}
    ]
}
```

---

## 6. Работа с LLM

### LLMClient реализация

1. **Инициализация:**
   - Асинхронный OpenAI клиент с base_url для OpenRouter
   - Системный промпт из конфига
   - Внедрение зависимости `ContextStorage` (Protocol)

2. **Управление контекстом:**
   - Использование абстракции `ContextStorage` вместо прямого dict
   - Добавление сообщений через `storage.add_message(user_id, role, content)`
   - Получение контекста через `storage.get_context(user_id)`
   - Очистка через `storage.reset_context(user_id)`

3. **Формирование запроса:**
   - Структура: system prompt + контекст из storage + новое сообщение
   - Формат OpenAI API: `[{"role": "system/user/assistant", "content": "..."}]`

4. **Вызов API:**
   - Асинхронный метод `await chat.completions.create()`
   - Параметры модели: по умолчанию (temperature, max_tokens)

5. **Обработка:**
   - Извлечение текста ответа
   - Сохранение ответа в контекст через storage
   - Логирование запросов/ответов
   - Обработка ошибок API

### ContextStorage Protocol

**Определение интерфейса:**
```python
from typing import Protocol, List, Dict

class ContextStorage(Protocol):
    """Протокол для хранилища контекста диалогов."""
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в контекст пользователя."""
        ...
    
    def get_context(self, user_id: int) -> List[Dict[str, str]]:
        """Получить историю сообщений для пользователя."""
        ...
    
    def reset_context(self, user_id: int) -> None:
        """Очистить контекст для пользователя."""
        ...
```

**Реализация in-memory:**
```python
class InMemoryContextStorage:
    """In-memory хранилище с ограничением по количеству сообщений."""
    
    def __init__(self, max_messages: int = 20) -> None:
        self._storage: Dict[int, List[Dict[str, str]]] = {}
        self._max_messages = max_messages
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        if user_id not in self._storage:
            self._storage[user_id] = []
        
        self._storage[user_id].append({"role": role, "content": content})
        
        # Автоматическое ограничение контекста
        if len(self._storage[user_id]) > self._max_messages:
            self._storage[user_id] = self._storage[user_id][-self._max_messages:]
```

**Готовность к масштабированию:**
- Легко заменить на `RedisContextStorage` или `DatabaseContextStorage`
- Изменения только в точке инициализации, LLMClient не меняется
- Следование Dependency Inversion Principle (SOLID)

---

## 7. Сценарии работы

### Основные команды

- `/start` - приветствие и описание возможностей бота
- `/help` - список доступных команд
- `/reset` - очистка истории диалога
- `/status` - проверка работоспособности бота

### Сценарий общения

1. Пользователь отправляет сообщение
2. Бот показывает статус "печатает..." (typing action)
3. Бот отправляет запрос в LLM с контекстом (последние 20 сообщений)
4. Бот возвращает ответ пользователю

### Обработка ошибок

- Технические ошибки логируются в файл
- Пользователю показываются дружественные сообщения

---

## 8. Подход к конфигурированию

### Файл .env

```ini
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token_here

# OpenRouter API
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# LLM Settings
SYSTEM_PROMPT=Ты - полезный AI-ассистент. Отвечай кратко и по делу.
MAX_CONTEXT_MESSAGES=20

# Logging
LOG_FILE_PATH=logs/bot.log
LOG_LEVEL=INFO
```

### Принципы

- Загрузка через `python-dotenv`
- Значения по умолчанию для необязательных параметров
- Строгая валидация обязательных полей (ConfigError)
- Immutable dataclass с методом `from_env()`
- Type hints для всех полей

---

## 9. Подход к логированию

### Настройка

- Стандартный модуль `logging`
- Вывод в файл `logs/bot.log` и консоль
- Ротация: по умолчанию (без настройки для MVP)
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Уровни

- `INFO` - старт/остановка, команды, сообщения
- `WARNING` - нештатные ситуации
- `ERROR` - ошибки API, исключения
- Уровень из конфига: `LOG_LEVEL`

### Что логируем

- Запуск/остановка бота
- Команды: `user_id`, команда
- Сообщения: `user_id`, первые 200 символов, длина
- Запросы/ответы LLM (сокращенно)
- Ошибки с stack trace

---

## 10. Качество кода и тестирование

### Автоматизация проверок

**CI Pipeline (make ci):**
```bash
make ci  # lint + format + type-check + test
```

**Обязательно перед коммитом:**
- `make lint` - проверка ruff (расширенные правила)
- `make format` - форматирование кода
- `make type-check` - проверка mypy strict mode
- `make test` - запуск тестов с coverage >= 85%

### Type Checking

**Mypy конфигурация:**
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

- Все публичные методы типизированы
- Strict mode включен
- Проверка перед каждым коммитом

### Тестирование

**Структура тестов:**
```
tests/
├── conftest.py              # Общие фикстуры (mock logger, config, etc.)
├── test_config.py           # Unit: Config загрузка, валидация
├── test_logger.py           # Unit: Logger настройка
├── test_context_storage.py  # Unit: InMemoryContextStorage
├── test_llm_client.py       # Unit: LLMClient с mock storage
├── test_bot.py              # Unit: TelegramBot команды и сообщения
└── integration/
    └── test_bot_flow.py     # Integration: полный сценарий работы
```

**Покрытие тестами:**
- **Unit тесты:** Все публичные методы классов
- **Edge cases:** Граничные условия, длинные сообщения, пустые значения
- **Error handling:** Обработка ошибок API, исключений, таймаутов
- **Integration:** Полный цикл работы бота
- **Coverage:** >= 85% (общий), >= 90% (новый код)

**Принципы тестирования:**
- **Arrange-Act-Assert** структура
- **Mock внешние зависимости** (Telegram API, OpenRouter API)
- **Изолированные тесты** (независимые друг от друга)
- **Быстрые тесты** (без реальных API вызовов в unit-тестах)

**Команды:**
```bash
make test              # запуск всех тестов
make test-cov          # с coverage report
pytest tests/unit/     # только unit тесты
pytest tests/integration/ --markers integration  # только интеграционные
```

### Стандарты кода

**Стиль и форматирование:**
- **PEP 8** - стиль кода (проверка через ruff)
- **Line length:** 100 символов
- **Форматирование:** автоматическое через `ruff format`

**Документация:**
- **Google Style** - формат docstrings
- **Type hints** - обязательно для всех публичных методов
- **Docstrings** - для всех классов и публичных методов

**Принципы дизайна:**
- **SOLID** - Single Responsibility, Dependency Inversion, etc.
- **DRY** - без дублирования кода
- **KISS** - простота превыше всего

**Инструменты контроля:**
- **Ruff** - 10+ категорий правил (E, F, W, I, N, UP, B, C4, SIM, RUF)
- **Mypy** - strict mode для проверки типов
- **Pytest** - тестирование с coverage report
- **Make** - автоматизация всех проверок

---

## 11. Процесс контроля качества

### CI Pipeline

**Локальная проверка (обязательна перед коммитом):**
```bash
make ci
```

**Что включает:**
1. `make lint` - проверка кода ruff
2. `make format` - форматирование кода
3. `make type-check` - проверка типов mypy
4. `make test` - запуск тестов с coverage

**Статус:** Все проверки должны проходить без ошибок

### Метрики качества

**Отслеживаемые метрики:**
- **Test Coverage:** >= 85% (текущий: 72% → цель: 85%+)
- **Mypy errors:** 0 (strict mode)
- **Ruff violations:** 0
- **Code duplication:** минимизирован
- **SOLID violations:** устранены

### Процесс рефакторинга

**Для улучшения кодовой базы используется:**
- `TASKLIST_TECH_DEBT.md` - план устранения технического долга
- `WORKFLOW_TECH_DEBT.md` - процесс работы с техническим долгом
- Инкрементальный подход (маленькие изменения)
- Обязательная проверка регрессии после каждого изменения

---

## Итого

Проект представляет собой **качественное MVP-решение** для проверки идеи LLM-ассистента в Telegram. Следуя принципам KISS, SOLID и DRY, мы создаем минимально необходимую функциональность без оверинжиниринга, с высоким качеством кода:

**Ключевые характеристики:**
- ✅ **Type-safe:** Полная типизация с mypy strict mode
- ✅ **Tested:** Coverage >= 85% с unit и integration тестами
- ✅ **Maintainable:** SOLID принципы, DRY, понятная архитектура
- ✅ **Scalable:** Protocol-based storage готов к замене
- ✅ **Quality-controlled:** Автоматизированные проверки через make ci

**Готовность:**
- 🚀 К продуктиву: MVP функционал работает
- 📈 К масштабированию: Архитектура поддерживает рост
- 🔧 К поддержке: Высокое качество кода и тесты

