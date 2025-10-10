"""Клиент для работы с LLM через OpenRouter API."""

import logging

from openai import AsyncOpenAI


class LLMClient:
    """Клиент для работы с LLM через OpenRouter API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        system_prompt: str,
        logger: logging.Logger,
    ):
        """
        Инициализация клиента.

        Args:
            api_key: OpenRouter API ключ
            model: Название модели (например, anthropic/claude-3.5-sonnet)
            base_url: Base URL для OpenRouter API
            system_prompt: Системный промпт
            logger: Логгер для событий
        """
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = system_prompt
        self.logger = logger

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
                f"Sending request to LLM: model={self.model}, "
                f"message_length={len(user_message)}"
            )

            # Вызов API
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages
            )

            # Извлекаем ответ
            answer = response.choices[0].message.content
            self.logger.info(f"Received response from LLM: length={len(answer)}")

            return answer

        except Exception as e:
            self.logger.error(f"Error calling LLM API: {e}", exc_info=True)
            raise

