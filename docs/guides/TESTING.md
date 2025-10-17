# 🧪 Стратегия тестирования

> Руководство по написанию и запуску тестов

---

## 📊 Текущее состояние

- **Тестов:** 49 unit тестов
- **Coverage:** 100% (без main.py)
- **Фреймворк:** pytest + pytest-asyncio + pytest-cov
- **Подход:** TDD (Test-Driven Development)

---

## 🎯 Принципы тестирования

### AAA Pattern (Arrange-Act-Assert)

```python
@pytest.mark.asyncio
async def test_method_name():
    """Test description."""
    # Arrange - подготовка данных
    user_id = 12345
    test_message = "test"

    # Act - выполнение действия
    result = await method(user_id, test_message)

    # Assert - проверка результата
    assert result == expected_value
```

### Именование тестов

```python
def test_<method>_<scenario>():
    """Test <method> <expected_behavior> when <condition>."""
```

**Примеры:**
- `test_cmd_start_returns_welcome_message()`
- `test_handle_message_empty_message()`
- `test_get_context_nonexistent_user()`

---

## 🔧 Настройка тестового окружения

### Фикстуры (conftest.py)

```python
# tests/conftest.py

@pytest.fixture
def mock_logger():
    """Mock logger для всех тестов."""
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def context_storage(mock_logger):
    """Реальный InMemoryContextStorage."""
    return InMemoryContextStorage(
        max_messages=20,
        max_users=1000,
        logger=mock_logger
    )

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
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.text = "Test message"
    message.chat = MagicMock()
    message.chat.id = 12345
    message.answer = AsyncMock()
    return message
```

**Принципы фикстур:**
- Одна фикстура = одна ответственность
- Реальные объекты для unit тестов (где возможно)
- Моки только для внешних зависимостей

---

## 📝 Типы тестов

### Unit тесты (основные)

Тестируют отдельные модули в изоляции.

**Пример: тест Config**

```python
def test_config_from_env_success(monkeypatch):
    """Test successful config loading from environment."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

    # Act
    config = Config.from_env()

    # Assert
    assert config.telegram_token == "test_token"
    assert config.openrouter_api_key == "test_key"
    assert config.bot_name == "SysTech AI Assistant"  # default
```

**Пример: тест TelegramBot команды**

```python
@pytest.mark.asyncio
async def test_cmd_start(bot, mock_message):
    """Test /start command returns welcome message."""
    # Arrange
    mock_message.from_user.username = "testuser"

    # Act
    await bot.cmd_start(mock_message)

    # Assert
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет, testuser" in call_args
```

---

### Edge Cases

Тестируют граничные условия и нетипичные сценарии.

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
    assert "Пожалуйста, напишите сообщение" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_too_long_message(bot, mock_message):
    """Test handling message longer than 4000 characters."""
    # Arrange
    mock_message.text = "a" * 5000

    # Act
    await bot.handle_message(mock_message)

    # Assert
    assert "слишком длинное" in mock_message.answer.call_args[0][0]
```

---

### Error Handling

Тестируют обработку ошибок.

```python
@pytest.mark.asyncio
async def test_get_response_api_error(llm_client):
    """Test handling API error gracefully."""
    # Arrange
    llm_client.client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )

    # Act & Assert
    with pytest.raises(Exception, match="API Error"):
        await llm_client.get_response("test message")
```

---

### Integration тесты (отложены)

Тестируют полный цикл работы нескольких компонентов вместе.

**Маркер в pyproject.toml:**
```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
]
```

**Пример (если будет создан):**
```python
@pytest.mark.integration
async def test_full_message_flow():
    """Test complete flow from message to LLM response."""
    # Arrange: создать все реальные компоненты
    # Act: отправить сообщение
    # Assert: проверить весь путь
    pass
```

---

## 🚀 Запуск тестов

### Базовые команды

```bash
# Все тесты
make test

# Только unit тесты (без integration)
make test-unit

# Integration тесты
make test-integration  # (сейчас пусто)

# С подробным выводом
pytest tests/ -v

# Конкретный файл
pytest tests/test_bot.py -v

# Конкретный тест
pytest tests/test_bot.py::test_cmd_start -v
```

### Coverage

```bash
# С coverage report
make test
# Показывает % coverage для каждого модуля

# Coverage report в терминале
pytest tests/ --cov=src --cov-report=term-missing

# HTML отчет
pytest tests/ --cov=src --cov-report=html
# Открыть: htmlcov/index.html
```

**Требования:**
- Общий coverage: >= 85%
- Новый код: >= 90%
- Критические модули: 100%

---

## 🎨 Стратегия моков

### Когда мокать?

✅ **Мокай:**
- Внешние API (Telegram, OpenRouter)
- I/O операции (network, filesystem)
- Время-зависимый код
- Дорогие вычисления

❌ **Не мокай:**
- Внутреннюю бизнес-логику
- Структуры данных (dataclass)
- Простые helper функции
- То, что и так быстро

### Примеры моков

**Mock AsyncOpenAI:**
```python
with patch("src.llm_client.AsyncOpenAI") as mock_openai:
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "LLM response"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
```

**Mock Telegram Message:**
```python
@pytest.fixture
def mock_message():
    message = MagicMock(spec=Message)
    message.from_user.id = 12345
    message.text = "Test"
    message.answer = AsyncMock()
    return message
```

---

## 🔄 TDD цикл (Red-Green-Refactor)

### 1. 🔴 RED - Написать failing test

```python
# tests/test_bot.py

@pytest.mark.asyncio
async def test_cmd_new_feature(bot, mock_message):
    """Test new feature command."""
    await bot.cmd_new_feature(mock_message)
    mock_message.answer.assert_called_once()
```

Запустить:
```bash
make test
# ❌ FAILED - AttributeError: no attribute 'cmd_new_feature'
```

---

### 2. 🟢 GREEN - Минимальная реализация

```python
# src/bot.py

async def cmd_new_feature(self, message: Message) -> None:
    """Handler for new feature."""
    await message.answer("Feature response")
```

Запустить:
```bash
make test
# ✅ PASSED - test_cmd_new_feature
```

---

### 3. ♻️ REFACTOR - Улучшить код

```python
# Улучшить если нужно
# Например: вынести текст в BotMessages
await message.answer(BotMessages.new_feature_text())
```

Проверить:
```bash
make ci
# ✅ All checks passed
```

---

## 📋 Структура тестового файла

```python
"""Tests for module_name."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from src.module_name import ClassName


class TestClassName:
    """Tests for ClassName."""

    def test_method_success_case(self):
        """Test method returns expected value on success."""
        # Arrange
        obj = ClassName()

        # Act
        result = obj.method()

        # Assert
        assert result == expected

    def test_method_edge_case(self):
        """Test method handles edge case correctly."""
        # ...

    def test_method_error_handling(self):
        """Test method raises error on invalid input."""
        with pytest.raises(ValueError):
            obj.method(invalid_input)


# Асинхронные тесты отдельно
@pytest.mark.asyncio
async def test_async_method():
    """Test async method behavior."""
    result = await async_method()
    assert result is not None
```

---

## ✅ Assertions

### Базовые assertions

```python
# Равенство
assert result == expected

# Наличие строки
assert "text" in response

# Исключение
with pytest.raises(ValueError, match="error message"):
    raise_error()

# Вызов mock
mock_method.assert_called_once()
mock_method.assert_called_with(param1, param2)
mock_method.assert_not_called()

# Количество вызовов
assert mock_method.call_count == 3
```

### Проверка async mock

```python
# AsyncMock для async функций
mock_method = AsyncMock(return_value="response")

# Вызов
result = await mock_method(param)

# Проверка
mock_method.assert_called_once_with(param)
assert result == "response"
```

---

## 🎯 Чек-лист теста

### Перед написанием
- [ ] Понятно что тестируется
- [ ] Понятен ожидаемый результат
- [ ] Выбран правильный тип теста (unit/integration)

### Во время написания
- [ ] Используется AAA pattern
- [ ] Понятное имя теста
- [ ] Один тест = один сценарий
- [ ] Используются фикстуры из conftest.py
- [ ] Async тесты помечены `@pytest.mark.asyncio`

### После написания
- [ ] Тест проходит
- [ ] Покрывает заявленный функционал
- [ ] Нет лишних assertions
- [ ] Coverage не упал

---

## 📊 Coverage метрики

### Текущий coverage

```bash
make test
```

```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/bot.py                     94      0   100%
src/config.py                  34      0   100%
src/context_storage.py         65      0   100%
src/llm_client.py              49      0   100%
src/logger.py                   9      0   100%
src/messages.py                11      0   100%
---------------------------------------------------------
TOTAL                         262      0   100%
```

**Исключения:**
- `src/main.py` - точка входа (тестируется через integration)

---

## 🔍 Отладка тестов

### Запуск одного теста с выводом

```bash
pytest tests/test_bot.py::test_cmd_start -v -s
```

**Флаги:**
- `-v` - подробный вывод
- `-s` - показать print() statements
- `-k` - фильтр по имени `pytest -k "test_cmd"`
- `--pdb` - запустить debugger при падении

### Просмотр логов в тестах

```python
def test_with_logs(caplog):
    """Test with log capture."""
    logger.info("Test log message")

    assert "Test log message" in caplog.text
```

---

## 🛠️ Полезные команды

```bash
# Быстрый запуск (без coverage)
pytest tests/

# С coverage и остановкой на первой ошибке
pytest tests/ --cov=src -x

# Только упавшие тесты из прошлого запуска
pytest --lf

# Parallel запуск (если установлен pytest-xdist)
pytest tests/ -n auto

# Показать самые медленные тесты
pytest tests/ --durations=10
```

---

## 📚 Примеры реальных тестов

### Config тест

```python
def test_config_from_env_missing_token(monkeypatch):
    """Test ConfigError when TELEGRAM_BOT_TOKEN is missing."""
    # Arrange
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    # Act & Assert
    with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN не найден"):
        Config.from_env()
```

### ContextStorage тест

```python
def test_add_message_trims_to_max(context_storage):
    """Test context is trimmed to max_messages limit."""
    # Arrange
    user_id = 12345

    # Act: добавить 25 сообщений
    for i in range(25):
        context_storage.add_message(user_id, "user", f"message {i}")

    # Assert: должно остаться только 20
    context = context_storage.get_context(user_id)
    assert len(context) == 20
    assert context[0]["content"] == "message 5"  # первые 5 удалены
```

### LLMClient тест

```python
@pytest.mark.asyncio
async def test_get_response_with_context_adds_to_storage(llm_client, context_storage):
    """Test response is added to context storage."""
    # Arrange
    user_id = 12345
    user_message = "test"
    llm_response = "LLM response"

    llm_client.client.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content=llm_response))]
        )
    )

    # Act
    await llm_client.get_response_with_context(user_id, user_message)

    # Assert
    context = context_storage.get_context(user_id)
    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == llm_response
```

---

## 🎓 Best Practices

### DO ✅

- Писать тесты ПЕРЕД кодом (TDD)
- Использовать AAA pattern
- Один тест = одна проверка
- Понятные имена тестов
- Использовать фикстуры из conftest.py
- Мокать внешние зависимости
- Проверять edge cases

### DON'T ❌

- Тестировать реализацию (тестируй поведение)
- Зависимость между тестами
- Хардкодить значения (использовать фикстуры)
- Игнорировать падающие тесты
- Снижать coverage
- Тестировать trivial код (геттеры)

---

## 📖 Дополнительная информация

- **Процессы разработки:** docs/guides/DEVELOPMENT.md
- **TDD Workflow:** .cursor/rules/workflow_tdd.mdc
- **QA Conventions:** .cursor/rules/qa_conventions.mdc
- **Pytest docs:** https://docs.pytest.org/

---

**Пиши тесты. Следуй TDD. Держи coverage >= 85%! 🧪**


