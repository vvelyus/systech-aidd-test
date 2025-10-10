"""Tests for TelegramBot module."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User

from src.bot import TelegramBot


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock()
    client.get_response_with_context = AsyncMock(return_value="LLM response")
    client.reset_context = MagicMock()
    return client


@pytest.fixture
def bot(mock_logger):
    """Create a TelegramBot instance without LLM."""
    with patch("src.bot.Bot"), patch("src.bot.Dispatcher"):
        bot_instance = TelegramBot(
            token="test_token", logger=mock_logger, llm_client=None
        )
        return bot_instance


@pytest.fixture
def bot_with_llm(mock_logger, mock_llm_client):
    """Create a TelegramBot instance with LLM."""
    with patch("src.bot.Bot"), patch("src.bot.Dispatcher"):
        bot_instance = TelegramBot(
            token="test_token", logger=mock_logger, llm_client=mock_llm_client
        )
        return bot_instance


@pytest.fixture
def mock_message():
    """Create a mock Message object."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.text = "Test message"
    message.chat = MagicMock()
    message.chat.id = 12345
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_cmd_start(bot, mock_message, mock_logger):
    """Test /start command handler."""
    await bot.cmd_start(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет" in call_args
    assert "test_user" in call_args
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_cmd_help(bot, mock_message, mock_logger):
    """Test /help command handler."""
    await bot.cmd_help(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/reset" in call_args
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_cmd_status(bot, mock_message, mock_logger):
    """Test /status command handler."""
    await bot.cmd_status(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Бот работает" in call_args
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_cmd_reset_with_llm(bot_with_llm, mock_message, mock_llm_client, mock_logger):
    """Test /reset command with LLM client."""
    await bot_with_llm.cmd_reset(mock_message)

    mock_llm_client.reset_context.assert_called_once_with(12345)
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "очищен" in call_args
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_cmd_reset_without_llm(bot, mock_message, mock_logger):
    """Test /reset command without LLM client."""
    await bot.cmd_reset(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "LLM не подключен" in call_args


@pytest.mark.asyncio
async def test_handle_message_with_llm(bot_with_llm, mock_message, mock_llm_client, mock_logger):
    """Test message handling with LLM client."""
    with patch.object(bot_with_llm.bot, "send_chat_action", new=AsyncMock()):
        await bot_with_llm.handle_message(mock_message)

        mock_llm_client.get_response_with_context.assert_called_once_with(
            user_id=12345, user_message="Test message"
        )
        mock_message.answer.assert_called_once_with("LLM response")
        mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_handle_message_without_llm(bot, mock_message, mock_logger):
    """Test message handling without LLM client (echo mode)."""
    with patch.object(bot.bot, "send_chat_action", new=AsyncMock()):
        await bot.handle_message(mock_message)

        mock_message.answer.assert_called_once_with("Эхо: Test message")
        mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_handle_empty_message(bot, mock_message):
    """Test handling empty message."""
    mock_message.text = ""

    with patch.object(bot.bot, "send_chat_action", new=AsyncMock()):
        await bot.handle_message(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Пожалуйста, напишите сообщение" in call_args


@pytest.mark.asyncio
async def test_handle_long_message(bot, mock_message, mock_logger):
    """Test handling very long message."""
    mock_message.text = "x" * 5000  # 5000 characters

    with patch.object(bot.bot, "send_chat_action", new=AsyncMock()):
        await bot.handle_message(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "слишком длинное" in call_args
        mock_logger.warning.assert_called()


@pytest.mark.asyncio
async def test_handle_message_error(bot_with_llm, mock_message, mock_llm_client, mock_logger):
    """Test error handling in message processing."""
    mock_llm_client.get_response_with_context.side_effect = Exception("API Error")

    with patch.object(bot_with_llm.bot, "send_chat_action", new=AsyncMock()):
        await bot_with_llm.handle_message(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "ошибка" in call_args
        mock_logger.error.assert_called()

