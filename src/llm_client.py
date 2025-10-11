"""Клиент для работы с LLM через OpenRouter API."""

import logging

from openai import AsyncOpenAI


class LLMClient:
    """Клиент для работы с LLM через OpenRouter API."""

    MAX_CONTEXT_MESSAGES = 20

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        system_prompt: str,
        logger: logging.Logger,
    ) -> None:
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
        self.history: dict[int, list[dict[str, str]]] = {}

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
            self._add_to_context(user_id, "user", user_message)

            # Получаем историю для пользователя
            context = self._get_context(user_id)

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
            self._add_to_context(user_id, "assistant", answer)

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
        if user_id in self.history:
            del self.history[user_id]
            self.logger.info(f"Context reset for user_id={user_id}")
        else:
            self.logger.info(f"No context to reset for user_id={user_id}")

    def _add_to_context(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст с ограничением.

        Если количество сообщений превышает MAX_CONTEXT_MESSAGES,
        оставляет только последние MAX_CONTEXT_MESSAGES.

        Args:
            user_id: ID пользователя
            role: Роль отправителя (user или assistant)
            content: Текст сообщения
        """
        if user_id not in self.history:
            self.history[user_id] = []

        self.history[user_id].append({"role": role, "content": content})

        # Ограничение: последние MAX_CONTEXT_MESSAGES сообщений
        if len(self.history[user_id]) > self.MAX_CONTEXT_MESSAGES:
            self.history[user_id] = self.history[user_id][-self.MAX_CONTEXT_MESSAGES :]
            self.logger.debug(
                f"Context trimmed to {self.MAX_CONTEXT_MESSAGES} messages for user_id={user_id}"
            )

    def _get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        return self.history.get(user_id, [])
