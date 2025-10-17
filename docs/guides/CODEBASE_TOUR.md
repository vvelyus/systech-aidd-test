# 🗺️ Тур по кодовой базе

> Путеводитель по коду с примерами и объяснениями

---

## 📂 Карта модулей

```
src/
├── main.py              # 🚀 Точка входа - инициализация всех компонентов
├── config.py            # ⚙️ Конфигурация - immutable dataclass
├── bot.py               # 🤖 Telegram обработчики - команды и сообщения
├── llm_client.py        # 🧠 OpenRouter интеграция - работа с LLM
├── context_storage.py   # 💾 Хранилище контекста - Protocol + реализация
├── messages.py          # 💬 Текстовые константы - все тексты бота
└── logger.py            # 📝 Логирование - настройка logger

prompts/
└── system_prompt.txt    # 🎭 Роль бота - системный промпт

tests/
├── conftest.py          # 🧪 Общие фикстуры для тестов
└── test_*.py            # 🧪 Unit тесты (49 тестов, 100% coverage)
```

---

## 🚀 Точка входа: main.py

### Что происходит при запуске

```python
async def main() -> None:
    """Точка входа приложения."""
    # 1. Загрузка конфигурации
    config = Config.from_env()  # .env → immutable Config

    # 2. Настройка логирования
    logger = setup_logger(config.log_file_path, config.log_level)

    # 3. Загрузка системного промпта из файла
    system_prompt = config.load_system_prompt()  # prompts/system_prompt.txt

    # 4. Создание хранилища контекста
    context_storage = InMemoryContextStorage(
        max_messages=20,
        max_users=1000,
        logger=logger
    )

    # 5. Создание LLM клиента с DI storage
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        model=config.openrouter_model,
        system_prompt=system_prompt,
        context_storage=context_storage,  # Dependency Injection
        logger=logger
    )

    # 6. Создание и запуск бота
    bot = TelegramBot(
        token=config.telegram_token,
        llm_client=llm_client,
        system_prompt=system_prompt,
        logger=logger
    )
    await bot.start()  # Polling mode
```

**Ключевые моменты:**
- Все компоненты создаются один раз при старте
- Dependency Injection для `ContextStorage`
- Graceful error handling с логированием

---

## ⚙️ Конфигурация: config.py

### Структура Config

```python
@dataclass(frozen=True)
class Config:
    """Immutable конфигурация приложения."""

    # Обязательные параметры
    telegram_token: str
    openrouter_api_key: str

    # Опциональные с defaults
    bot_name: str = "SysTech AI Assistant"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    system_prompt_file: str = "prompts/system_prompt.txt"
    max_context_messages: int = 20
    log_level: str = "INFO"
    # ... другие
```

### Как использовать

```python
# Загрузка из .env
config = Config.from_env()

# Доступ к полям (read-only)
print(config.bot_name)  # "SysTech AI Assistant"

# Попытка изменить -> FrozenInstanceError
config.bot_name = "New"  # ❌ Ошибка!

# Загрузка системного промпта
prompt = config.load_system_prompt()  # Читает prompts/system_prompt.txt
```

**Ключевые особенности:**
- `frozen=True` - immutability (thread-safe)
- `from_env()` - factory method с валидацией
- `ConfigError` при отсутствии обязательных полей

---

## 🤖 Telegram бот: bot.py

### Структура TelegramBot

```python
class TelegramBot:
    """Обработчик Telegram команд и сообщений."""

    def __init__(
        self,
        token: str,
        logger: logging.Logger,
        system_prompt: str,
        llm_client: Optional[LLMClient] = None,
        bot_name: str = "AI Assistant"
    ):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()  # aiogram 3.x
        self.llm_client = llm_client
        # ...
        self._register_handlers()
```

### Команды бота

```python
@log_command  # Декоратор для автоматического логирования
async def cmd_start(self, message: Message) -> None:
    """Обработчик /start."""
    username = message.from_user.username or "user"
    await message.answer(BotMessages.welcome(username, self.bot_name))

@log_command
async def cmd_reset(self, message: Message) -> None:
    """Обработчик /reset - очистка контекста."""
    user_id = message.from_user.id
    self.llm_client.reset_context(user_id)
    await message.answer(BotMessages.context_reset_success())
```

### Обработка сообщений

```python
async def handle_message(self, message: Message) -> None:
    """Обработка текстовых сообщений."""
    text = message.text or ""

    # Edge case: пустое сообщение
    if len(text) < 1:
        await message.answer(BotMessages.empty_message())
        return

    # Edge case: слишком длинное сообщение
    if len(text) > 4000:
        await message.answer(BotMessages.message_too_long())
        return

    # Показать "печатает..."
    await self.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Получить ответ от LLM
    response = await self.llm_client.get_response_with_context(
        user_id=message.from_user.id,
        user_message=text
    )

    await message.answer(response)
```

### Декоратор @log_command

```python
def log_command(func):
    """Автоматическое логирование команд."""
    @wraps(func)
    async def wrapper(self, message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        command = message.text or func.__name__
        self.logger.info(f"Command {command} from user_id={user_id}, username={username}")
        await func(self, message)
    return wrapper
```

**Применение DRY:** Один декоратор вместо дублирования логирования в каждой команде.

---

## 🧠 LLM клиент: llm_client.py

### Структура LLMClient

```python
class LLMClient:
    """Клиент для OpenRouter API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        system_prompt: str,
        logger: logging.Logger,
        context_storage: ContextStorage  # Protocol (DI)
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.context_storage = context_storage  # Pluggable storage
        # ...
```

### Работа с контекстом

```python
async def get_response_with_context(self, user_id: int, user_message: str) -> str:
    """Получить ответ с учетом истории диалога."""

    # 1. Добавить сообщение пользователя в историю
    self.context_storage.add_message(user_id, "user", user_message)

    # 2. Получить историю (последние 20 сообщений)
    context = self.context_storage.get_context(user_id)

    # 3. Сформировать запрос с системным промптом и историей
    messages = [
        {"role": "system", "content": self.system_prompt},
        *context  # Распаковать историю
    ]

    # 4. Вызов OpenRouter API
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=messages
    )

    # 5. Сохранить ответ в историю
    answer = response.choices[0].message.content
    self.context_storage.add_message(user_id, "assistant", answer)

    return answer
```

**Ключевые особенности:**
- Полностью асинхронный
- Использует абстракцию `ContextStorage` (не знает о реализации)
- Автоматическое управление контекстом

---

## 💾 Хранилище контекста: context_storage.py

### Protocol определение

```python
from typing import Protocol, List, Dict

class ContextStorage(Protocol):
    """Интерфейс для хранилища контекста."""

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в контекст пользователя."""
        ...

    def get_context(self, user_id: int) -> List[Dict[str, str]]:
        """Получить историю для пользователя."""
        ...

    def reset_context(self, user_id: int) -> None:
        """Очистить контекст для пользователя."""
        ...
```

### Реализация: InMemoryContextStorage

```python
class InMemoryContextStorage:
    """In-memory хранилище с лимитами."""

    def __init__(
        self,
        max_messages: int = 20,
        max_users: int = 1000,
        logger: Optional[logging.Logger] = None
    ):
        self._storage: Dict[int, List[Dict[str, str]]] = {}
        self._max_messages = max_messages
        self._max_users = max_users

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение с автоматическим trimming."""
        if user_id not in self._storage:
            self._storage[user_id] = []

        # Добавить сообщение
        self._storage[user_id].append({"role": role, "content": content})

        # Автоматическое ограничение до max_messages
        if len(self._storage[user_id]) > self._max_messages:
            self._storage[user_id] = self._storage[user_id][-self._max_messages:]

        # LRU стратегия при превышении max_users
        self._evict_lru_if_needed()
```

**Почему Protocol?**
- Легко заменить реализацию (Redis, Database)
- Не нужно наследование (structural typing)
- Mypy проверит соответствие интерфейсу

**Пример замены:**

```python
# Добавить новый файл redis_storage.py
class RedisContextStorage:
    """Redis реализация."""

    def add_message(self, user_id: int, role: str, content: str) -> None:
        # Redis логика
        pass

    # ... другие методы Protocol

# В main.py изменить одну строку:
context_storage = RedisContextStorage(redis_url=config.redis_url)
# Все остальное работает без изменений!
```

---

## 💬 Текстовые константы: messages.py

### Структура BotMessages

```python
class BotMessages:
    """Централизованное хранилище текстов бота."""

    @staticmethod
    def welcome(username: str, bot_name: str) -> str:
        """Приветственное сообщение."""
        return f"""
👋 Привет, {username}!

Я {bot_name} - твой AI-помощник...
"""

    @staticmethod
    def help_text() -> str:
        """Список команд."""
        return """
📋 Доступные команды:

/start - Начать работу
/help - Показать это сообщение
...
"""
```

**Преимущества:**
- Все тексты в одном месте
- Легко изменить формулировки
- Простая локализация (если понадобится)
- SRP - только тексты

---

## 🧪 Тесты: структура и фикстуры

### Общие фикстуры (conftest.py)

```python
@pytest.fixture
def mock_logger():
    """Mock logger для всех тестов."""
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def context_storage(mock_logger):
    """Реальный InMemoryContextStorage для тестов."""
    return InMemoryContextStorage(max_messages=20, max_users=1000, logger=mock_logger)

@pytest.fixture
def llm_client(mock_logger, context_storage):
    """Реальный LLMClient с мокнутым AsyncOpenAI."""
    with patch("src.llm_client.AsyncOpenAI"):
        return LLMClient(
            api_key="test_key",
            model="test_model",
            base_url="https://test.api",
            system_prompt="Test prompt",
            logger=mock_logger,
            context_storage=context_storage
        )

@pytest.fixture
def mock_message():
    """Mock Telegram Message."""
    message = MagicMock(spec=Message)
    message.from_user.id = 12345
    message.text = "Test message"
    message.answer = AsyncMock()
    return message
```

### Пример теста

```python
@pytest.mark.asyncio
async def test_handle_empty_message(bot, mock_message):
    """Test handling empty message."""
    # Arrange
    mock_message.text = ""

    # Act
    await bot.handle_message(mock_message)

    # Assert
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Пожалуйста, напишите сообщение" in call_args
```

---

## 🔍 Навигация по коду: FAQ

### Как добавить новую команду?

1. Добавить метод в `TelegramBot`:
```python
@log_command
async def cmd_mycommand(self, message: Message) -> None:
    await message.answer("My response")
```

2. Зарегистрировать в `_register_handlers()`:
```python
self.dp.message.register(self.cmd_mycommand, Command("mycommand"))
```

3. Добавить текст в `BotMessages`:
```python
@staticmethod
def mycommand_text() -> str:
    return "My command response"
```

4. Добавить тест в `test_bot.py`:
```python
async def test_cmd_mycommand(bot, mock_message):
    await bot.cmd_mycommand(mock_message)
    mock_message.answer.assert_called_once()
```

---

### Как изменить роль бота?

Просто отредактировать файл:

```bash
vim prompts/system_prompt.txt
```

Содержимое:
```
Ты - [Новая роль бота].

Твоя специализация: [описание]

Основные функции:
- функция 1
- функция 2

Стиль общения: [стиль]
```

Перезапустить:
```bash
make run
```

---

### Где логи?

- **Файл:** `logs/bot.log` - полная история
- **Консоль:** real-time вывод при `make run`
- **Формат:** `2025-10-16 12:00:00 - systech_bot - INFO - Message`

---

### Как запустить конкретный тест?

```bash
# Один файл
pytest tests/test_bot.py -v

# Один тест
pytest tests/test_bot.py::test_cmd_start -v

# По метке
pytest -m "not integration" -v

# С coverage для одного файла
pytest tests/test_bot.py --cov=src.bot --cov-report=term
```

---

## 📊 Метрики кодовой базы

- **Модули:** 7 (src) + 1 (prompts)
- **Тесты:** 49 unit тестов
- **Coverage:** 100%
- **Строк кода:** ~600 (src)
- **Публичных методов:** ~20
- **Классов:** 6

---

## 🎯 Типичные сценарии изменений

### Добавить новую модель LLM

Изменить `.env`:
```ini
OPENROUTER_MODEL=google/gemini-pro
```

Перезапустить - готово!

---

### Изменить лимит контекста

Изменить `.env`:
```ini
MAX_CONTEXT_MESSAGES=50
```

---

### Добавить новое хранилище

1. Создать файл `src/redis_storage.py`
2. Реализовать Protocol `ContextStorage`
3. Изменить `main.py`:
```python
context_storage = RedisContextStorage(...)  # вместо InMemoryContextStorage
```

---

## 📚 Дополнительная информация

- **Архитектура:** docs/guides/ARCHITECTURE.md
- **Процессы разработки:** docs/guides/DEVELOPMENT.md
- **Тестирование:** docs/guides/TESTING.md
- **Техническое видение:** docs/VISION.md


