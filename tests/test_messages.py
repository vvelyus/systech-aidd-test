"""Tests for BotMessages module."""

from src.messages import BotMessages


def test_bot_messages_role():
    """Test role message formatting with system prompt."""
    # Arrange
    system_prompt = """Ты - Технический консультант SysTech.

Твоя специализация: Помощь разработчикам в технических вопросах.

Основные функции:
- Анализ кода
- Помощь с отладкой
- Консультации

Стиль общения: Профессиональный."""

    # Act
    result = BotMessages.role(system_prompt)

    # Assert
    assert result
    assert "Технический консультант" in result
    assert len(result) > 50
    assert "🎭" in result or "роль" in result.lower()


def test_bot_messages_role_extracts_first_line():
    """Test that role message extracts bot name from first line."""
    # Arrange
    system_prompt = "Ты - AI Помощник.\n\nТвоя специализация: помощь с задачами."

    # Act
    result = BotMessages.role(system_prompt)

    # Assert
    assert "AI Помощник" in result


def test_bot_messages_role_handles_short_prompt():
    """Test role message with short system prompt."""
    # Arrange
    system_prompt = "Ты - Бот."

    # Act
    result = BotMessages.role(system_prompt)

    # Assert
    assert result
    assert "Бот" in result
