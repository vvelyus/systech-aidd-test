"""Tests for TelegramBot module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot import TelegramBot


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
    assert "/role" in call_args
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


@pytest.mark.asyncio
async def test_cmd_start_no_user(bot):
    """Test /start command when from_user is None."""
    # Create message without from_user
    mock_msg = MagicMock()
    mock_msg.from_user = None
    mock_msg.answer = AsyncMock()

    # Should return early without calling answer
    await bot.cmd_start(mock_msg)

    mock_msg.answer.assert_not_called()


@pytest.mark.asyncio
async def test_cmd_help_no_user(bot):
    """Test /help command when from_user is None."""
    # Create message without from_user
    mock_msg = MagicMock()
    mock_msg.from_user = None
    mock_msg.answer = AsyncMock()

    # Should return early without calling answer
    await bot.cmd_help(mock_msg)

    mock_msg.answer.assert_not_called()


@pytest.mark.asyncio
async def test_cmd_status_no_user(bot):
    """Test /status command when from_user is None."""
    # Create message without from_user
    mock_msg = MagicMock()
    mock_msg.from_user = None
    mock_msg.answer = AsyncMock()

    # Should return early without calling answer
    await bot.cmd_status(mock_msg)

    mock_msg.answer.assert_not_called()


@pytest.mark.asyncio
async def test_cmd_reset_no_user(bot):
    """Test /reset command when from_user is None."""
    # Create message without from_user
    mock_msg = MagicMock()
    mock_msg.from_user = None
    mock_msg.answer = AsyncMock()

    # Should return early without calling answer
    await bot.cmd_reset(mock_msg)

    mock_msg.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_no_user(bot):
    """Test message handling when from_user is None."""
    # Create message without from_user
    mock_msg = MagicMock()
    mock_msg.from_user = None
    mock_msg.answer = AsyncMock()

    # Should return early without calling answer
    await bot.handle_message(mock_msg)

    mock_msg.answer.assert_not_called()


@pytest.mark.asyncio
async def test_start_polling_success(bot, mock_logger):
    """Test bot start in polling mode."""
    with patch.object(bot.dp, "start_polling", new=AsyncMock()) as mock_poll:
        with patch.object(bot.bot, "session") as mock_session:
            mock_session.close = AsyncMock()

            # Act
            await bot.start()

            # Assert
            mock_poll.assert_called_once_with(bot.bot)
            mock_session.close.assert_called_once()
            mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_start_polling_error(bot, mock_logger):
    """Test bot start with error in polling."""
    with patch.object(bot.dp, "start_polling", new=AsyncMock(side_effect=Exception("Polling error"))):
        with patch.object(bot.bot, "session") as mock_session:
            mock_session.close = AsyncMock()

            # Should propagate exception but still close session
            with pytest.raises(Exception, match="Polling error"):
                await bot.start()

            mock_session.close.assert_called_once()
            mock_logger.error.assert_called()


# Tests for /role command


@pytest.fixture
def bot_with_role(mock_logger):
    """Create a TelegramBot instance with system prompt."""
    with patch("src.bot.Bot"), patch("src.bot.Dispatcher"):
        bot_instance = TelegramBot(
            token="test_token",
            logger=mock_logger,
            system_prompt="Ты - Технический консультант SysTech.",
            llm_client=None,
        )
        return bot_instance


@pytest.mark.asyncio
async def test_cmd_role_displays_role(bot_with_role, mock_message, mock_logger):
    """Test /role command displays bot role."""
    await bot_with_role.cmd_role(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Технический консультант" in call_args
    assert "🎭" in call_args
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_cmd_role_no_user(bot_with_role, mock_message):
    """Test /role command with no user in message."""
    mock_message.from_user = None

    await bot_with_role.cmd_role(mock_message)

    # Should not call answer if no user
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_cmd_role_with_custom_prompt(mock_logger, mock_message):
    """Test /role command with custom system prompt."""
    with patch("src.bot.Bot"), patch("src.bot.Dispatcher"):
        custom_bot = TelegramBot(
            token="test_token",
            logger=mock_logger,
            system_prompt="Ты - AI Помощник.\n\nТвоя специализация: помощь.",
            llm_client=None,
        )

        await custom_bot.cmd_role(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "AI Помощник" in call_args


# Tests for user data saving (Sprint S2)


@pytest.fixture
def bot_with_db_manager(mock_logger):
    """Create a TelegramBot instance with db_manager."""
    from src.models import User

    mock_db_manager = MagicMock()
    # Make upsert_user an AsyncMock that returns a User
    mock_user = User(telegram_id=12345, username="test_user")
    mock_db_manager.upsert_user = AsyncMock(return_value=mock_user)

    with patch("src.bot.Bot"), patch("src.bot.Dispatcher"):
        bot_instance = TelegramBot(
            token="test_token",
            logger=mock_logger,
            llm_client=None,
            db_manager=mock_db_manager,
        )
        return bot_instance


@pytest.mark.asyncio
async def test_save_user_data_success(bot_with_db_manager, mock_message):
    """Test _save_user_data successfully saves user data."""
    await bot_with_db_manager._save_user_data(mock_message)

    bot_with_db_manager.db_manager.upsert_user.assert_called_once_with(
        telegram_id=12345,
        username="test_user",
        first_name="Test",
        last_name="User",
        language_code="en",
    )


@pytest.mark.asyncio
async def test_save_user_data_no_user(bot_with_db_manager, mock_message):
    """Test _save_user_data with no user in message."""
    mock_message.from_user = None

    await bot_with_db_manager._save_user_data(mock_message)

    # Should not call upsert_user if no user
    bot_with_db_manager.db_manager.upsert_user.assert_not_called()


@pytest.mark.asyncio
async def test_save_user_data_no_db_manager(bot, mock_message):
    """Test _save_user_data without db_manager."""
    # bot fixture has no db_manager
    await bot._save_user_data(mock_message)

    # Should not raise an error, just return early


@pytest.mark.asyncio
async def test_save_user_data_handles_exception(bot_with_db_manager, mock_message, mock_logger):
    """Test _save_user_data handles database exceptions gracefully."""
    bot_with_db_manager.db_manager.upsert_user.side_effect = Exception("DB error")

    # Should not raise exception
    await bot_with_db_manager._save_user_data(mock_message)

    # Should log error
    mock_logger.error.assert_called_once()
    call_args = str(mock_logger.error.call_args)
    assert "Failed to save user data" in call_args


@pytest.mark.asyncio
async def test_cmd_start_saves_user_data(bot_with_db_manager, mock_message):
    """Test /start command saves user data."""
    await bot_with_db_manager.cmd_start(mock_message)

    # Should save user data
    bot_with_db_manager.db_manager.upsert_user.assert_called_once()
    # And send welcome message
    mock_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_saves_user_data(bot_with_db_manager, mock_message):
    """Test message handling saves user data."""
    with patch.object(bot_with_db_manager.bot, "send_chat_action", new=AsyncMock()):
        await bot_with_db_manager.handle_message(mock_message)

        # Should save user data
        bot_with_db_manager.db_manager.upsert_user.assert_called_once()
        # And send response
        mock_message.answer.assert_called_once()
