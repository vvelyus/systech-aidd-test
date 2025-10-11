"""Telegram бот на базе aiogram."""

import logging
from typing import TYPE_CHECKING, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

if TYPE_CHECKING:
    from llm_client import LLMClient


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

    async def cmd_start(self, message: Message) -> None:
        """
        Обработчик команды /start.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        username = message.from_user.username or "user"

        self.logger.info(f"Command /start from user_id={user_id}, username={username}")

        welcome_text = (
            f"👋 Привет, {username}!\n\n"
            f"Я {self.bot_name} — AI-бот, который может общаться с тобой через LLM модели.\n\n"
            "🎯 Мои возможности:\n"
            "• Общение на естественном языке\n"
            "• Запоминание контекста диалога\n"
            "• Помощь с вопросами и задачами\n\n"
            "💬 Просто напиши мне что-нибудь, и я постараюсь помочь!\n\n"
            "Используй /help чтобы увидеть доступные команды."
        )

        await message.answer(welcome_text)

    async def cmd_help(self, message: Message) -> None:
        """
        Обработчик команды /help.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        self.logger.info(f"Command /help from user_id={user_id}")

        help_text = (
            "📚 Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Проверить работоспособность\n"
            "/reset - Очистить контекст диалога\n\n"
            "💡 Как пользоваться:\n"
            "Просто напиши мне любое сообщение, и я отвечу! "
            "Я запоминаю контекст нашего разговора (последние 20 сообщений), "
            "поэтому можешь задавать уточняющие вопросы.\n\n"
            "🔄 Если хочешь начать диалог заново, используй /reset"
        )

        await message.answer(help_text)

    async def cmd_status(self, message: Message) -> None:
        """
        Обработчик команды /status.

        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        self.logger.info(f"Command /status from user_id={user_id}")

        status_text = "✅ Бот работает!\n\nВсе системы функционируют в штатном режиме."

        await message.answer(status_text)

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
        self.logger.info(f"Command /reset from user_id={user_id}")

        if self.llm_client:
            self.llm_client.reset_context(user_id)
            await message.answer("✅ Контекст диалога очищен. Начинаем с чистого листа!")
        else:
            await message.answer("⚠️ LLM не подключен, контекст не используется.")

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
            await message.answer("Пожалуйста, напишите сообщение с текстом.")
            return

        # Edge case: очень длинное сообщение (больше 4000 символов)
        if text_length > 4000:
            self.logger.warning(f"Message too long from user_id={user_id}, length={text_length}")
            await message.answer(
                "Ваше сообщение слишком длинное (больше 4000 символов). "
                "Пожалуйста, сократите его и попробуйте еще раз."
            )
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
                response = f"Эхо: {text}"
                self.logger.info(f"Sent echo response to user_id={user_id}")

            await message.answer(response)

        except Exception as e:
            # Обработка ошибок с дружественным сообщением
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте еще раз позже."
            )

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
