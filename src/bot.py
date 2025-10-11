"""Telegram бот на базе aiogram."""

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from src.messages import BotMessages

if TYPE_CHECKING:
    from src.llm_client import LLMClient


def log_command(
    func: Callable[["TelegramBot", Message], Awaitable[None]],
) -> Callable[["TelegramBot", Message], Awaitable[None]]:
    """
    Декоратор для логирования команд бота.

    Автоматически логирует информацию о пользователе и команде
    перед выполнением обработчика.

    Args:
        func: Асинхронная функция-обработчик команды

    Returns:
        Callable: Обёрнутая функция с логированием
    """

    @wraps(func)
    async def wrapper(self: "TelegramBot", message: Message) -> None:
        if message.from_user:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            command = message.text or func.__name__
            self.logger.info(f"Command {command} from user_id={user_id}, username={username}")
        await func(self, message)

    return wrapper


class TelegramBot:
    """Telegram бот на базе aiogram."""

    def __init__(
        self,
        token: str,
        logger: logging.Logger,
        llm_client: Optional["LLMClient"] = None,
        bot_name: str = "AI Assistant",
    ) -> None:
        """
        Инициализация бота.

        Args:
            token: Telegram Bot API токен
            logger: Логгер для событий
            llm_client: Клиент для работы с LLM (опционально)
            bot_name: Имя бота для отображения в сообщениях
        """
        self.logger = logger
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self.bot_name = bot_name

        # Регистрируем обработчики
        self._register_handlers()

        if self.llm_client:
            self.logger.info("TelegramBot initialized with LLM support")
        else:
            self.logger.info("TelegramBot initialized without LLM (echo mode)")

    def _register_handlers(self) -> None:
        """Регистрирует обработчики команд и сообщений."""
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_status, Command("status"))
        self.dp.message.register(self.cmd_reset, Command("reset"))
        self.dp.message.register(self.handle_message, F.text)

    @log_command
    async def cmd_start(self, message: Message) -> None:
        """
        Обработчик команды /start.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        username = message.from_user.username or "user"
        await message.answer(BotMessages.welcome(username, self.bot_name))

    @log_command
    async def cmd_help(self, message: Message) -> None:
        """
        Обработчик команды /help.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        await message.answer(BotMessages.help_text())

    @log_command
    async def cmd_status(self, message: Message) -> None:
        """
        Обработчик команды /status.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        await message.answer(BotMessages.status())

    @log_command
    async def cmd_reset(self, message: Message) -> None:
        """
        Обработчик команды /reset.

        Очищает контекст диалога для пользователя.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id

        if self.llm_client:
            self.llm_client.reset_context(user_id)
            await message.answer(BotMessages.context_reset_success())
        else:
            await message.answer(BotMessages.llm_not_connected())

    async def handle_message(self, message: Message) -> None:
        """
        Обработчик текстовых сообщений.

        Показывает индикатор печати и отправляет ответ от LLM
        или эхо-ответ, если LLM не настроен.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        text = message.text or ""
        text_length = len(text)

        # Edge case: пустое или очень короткое сообщение
        if text_length < 1:
            await message.answer(BotMessages.empty_message())
            return

        # Edge case: очень длинное сообщение (больше 4000 символов)
        if text_length > 4000:
            self.logger.warning(f"Message too long from user_id={user_id}, length={text_length}")
            await message.answer(BotMessages.message_too_long())
            return

        text_preview = text[:200]

        self.logger.info(
            f"Message from user_id={user_id}, length={text_length}, text: {text_preview}..."
        )

        # Показываем индикатор "печатает..."
        await self.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        try:
            if self.llm_client:
                # Получаем ответ от LLM с учетом контекста
                response = await self.llm_client.get_response_with_context(
                    user_id=user_id, user_message=text
                )
                self.logger.info(f"Sent LLM response to user_id={user_id}")
            else:
                # Fallback на echo если LLM не настроен
                response = BotMessages.echo(text)
                self.logger.info(f"Sent echo response to user_id={user_id}")

            await message.answer(response)

        except Exception as e:
            # Обработка ошибок с дружественным сообщением
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            await message.answer(BotMessages.processing_error())

    async def start(self) -> None:
        """Запуск бота в режиме polling."""
        self.logger.info("Starting bot in polling mode...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            self.logger.error(f"Bot error: {e}", exc_info=True)
            raise
        finally:
            await self.bot.session.close()
