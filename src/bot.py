"""Telegram бот на базе aiogram."""

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message


class TelegramBot:
    """Telegram бот на базе aiogram."""

    def __init__(self, token: str, logger: logging.Logger):
        """
        Инициализация бота.

        Args:
            token: Telegram Bot API токен
            logger: Логгер для событий
        """
        self.logger = logger
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        # Регистрируем обработчики
        self._register_handlers()

        self.logger.info("TelegramBot initialized")

    def _register_handlers(self):
        """Регистрирует обработчики команд и сообщений."""
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_status, Command("status"))
        self.dp.message.register(self.handle_message, F.text)

    async def cmd_start(self, message: Message):
        """
        Обработчик команды /start.

        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id
        username = message.from_user.username or "user"

        self.logger.info(f"Command /start from user_id={user_id}, username={username}")

        welcome_text = (
            f"👋 Привет, {username}!\n\n"
            "Я AI-ассистент, созданный для помощи в различных вопросах.\n\n"
            "Просто напиши мне сообщение, и я постараюсь помочь!\n\n"
            "Используй /help для списка доступных команд."
        )

        await message.answer(welcome_text)

    async def cmd_help(self, message: Message):
        """
        Обработчик команды /help.

        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id
        self.logger.info(f"Command /help from user_id={user_id}")

        help_text = (
            "📚 Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Проверить работоспособность бота\n\n"
            "Просто напиши мне любое сообщение, и я отвечу!"
        )

        await message.answer(help_text)

    async def cmd_status(self, message: Message):
        """
        Обработчик команды /status.

        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id
        self.logger.info(f"Command /status from user_id={user_id}")

        status_text = "✅ Бот работает!\n\nВсе системы функционируют в штатном режиме."

        await message.answer(status_text)

    async def handle_message(self, message: Message):
        """
        Обработчик текстовых сообщений (echo).

        Показывает индикатор печати и отправляет эхо-ответ.
        В следующих итерациях здесь будет интеграция с LLM.

        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id
        text = message.text or ""
        text_preview = text[:200]
        text_length = len(text)

        self.logger.info(
            f"Message from user_id={user_id}, length={text_length}, text: {text_preview}..."
        )

        # Показываем индикатор "печатает..."
        await self.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # Echo - повторяем сообщение пользователя
        response = f"Эхо: {text}"

        await message.answer(response)
        self.logger.info(f"Sent echo response to user_id={user_id}")

    async def start(self):
        """Запуск бота в режиме polling."""
        self.logger.info("Starting bot in polling mode...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            self.logger.error(f"Bot error: {e}", exc_info=True)
            raise
        finally:
            await self.bot.session.close()
