"""Клиент для работы с LLM через OpenRouter API."""

import logging

from openai import AsyncOpenAI

from src.context_storage import ContextStorage


class LLMClient:
    """
    Клиент для работы с LLM через OpenRouter API.

    Использует pluggable ContextStorage для хранения истории диалогов,
    что позволяет легко заменить реализацию хранилища (например, на Redis).
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        system_prompt: str,
        logger: logging.Logger,
        context_storage: ContextStorage,
    ) -> None:
        """
        Инициализация клиента.

        Args:
            api_key: OpenRouter API ключ
            model: Название модели (например, anthropic/claude-3.5-sonnet)
            base_url: Base URL для OpenRouter API
            system_prompt: Системный промпт
            logger: Логгер для событий
            context_storage: Хранилище контекста диалогов
        """
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = system_prompt
        self.logger = logger
        self.context_storage = context_storage

        self.logger.info(f"LLMClient initialized with model: {model}")

    async def get_response(self, user_message: str) -> str:
        """
        Получить ответ от LLM на одиночное сообщение.

        Формирует запрос с системным промптом и сообщением пользователя,
        отправляет в LLM и возвращает ответ.

        Args:
            user_message: Сообщение пользователя

        Returns:
            str: Ответ от LLM

        Raises:
            Exception: При ошибках API
        """
        try:
            # Формируем запрос
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ]

            self.logger.info(
                f"Sending request to LLM: model={self.model}, message_length={len(user_message)}"
            )

            # Вызов API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
            )

            # Извлекаем ответ
            answer = response.choices[0].message.content
            if not answer:
                raise ValueError("Empty response from LLM")
            self.logger.info(f"Received response from LLM: length={len(answer)}")

            return answer

        except Exception as e:
            self.logger.error(f"Error calling LLM API: {e}", exc_info=True)
            raise

    async def get_response_with_context(self, user_id: int, user_message: str) -> str:
        """
        Получить ответ от LLM с учетом контекста диалога.

        Добавляет сообщение пользователя в историю, формирует запрос
        с учетом предыдущих сообщений, получает ответ и сохраняет его
        в историю.

        Args:
            user_id: ID пользователя
            user_message: Сообщение пользователя

        Returns:
            str: Ответ от LLM

        Raises:
            Exception: При ошибках API
        """
        try:
            # Добавляем сообщение пользователя в контекст
            self.context_storage.add_message(user_id, "user", user_message)

            # Получаем историю для пользователя
            context = self.context_storage.get_context(user_id)

            # Формируем запрос с системным промптом и историей
            messages = [
                {"role": "system", "content": self.system_prompt},
                *context,
            ]

            self.logger.info(
                f"Sending request to LLM with context: user_id={user_id}, "
                f"model={self.model}, context_length={len(context)}"
            )

            # Вызов API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
            )

            # Извлекаем и сохраняем ответ в контекст
            answer = response.choices[0].message.content
            if not answer:
                raise ValueError("Empty response from LLM")
            self.context_storage.add_message(user_id, "assistant", answer)

            self.logger.info(f"Received response from LLM: user_id={user_id}, length={len(answer)}")

            return answer

        except Exception as e:
            self.logger.error(
                f"Error calling LLM API with context for user_id={user_id}: {e}",
                exc_info=True,
            )
            raise

    def reset_context(self, user_id: int) -> None:
        """
        Очистить контекст диалога для пользователя.

        Args:
            user_id: ID пользователя
        """
        self.context_storage.reset_context(user_id)
