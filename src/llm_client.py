"""Клиент для работы с LLM через OpenRouter API."""

import asyncio
import logging

from openai import AsyncOpenAI, RateLimitError

from src.context_storage import ContextStorage


class RateLimitExceededError(Exception):
    """Ошибка когда превышен лимит API (429)."""

    def __init__(self, message: str, retry_after: int | None = None):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry (if available)
        """
        super().__init__(message)
        self.retry_after = retry_after


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
        self.max_retries = 5
        self.base_delay = 1.0  # seconds

        self.logger.info(f"LLMClient initialized with model: {model}")

    async def _api_call_with_retry(self, messages: list, max_retries: int = None) -> str:
        """
        Выполнить API запрос с retry при rate limit (429).

        Args:
            messages: Список сообщений для API
            max_retries: Максимальное количество повторов

        Returns:
            str: Ответ от LLM

        Raises:
            RateLimitExceededError: При превышении лимита (429)
            Exception: При других ошибках (не 429)
        """
        if max_retries is None:
            max_retries = self.max_retries

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
            )
            answer = response.choices[0].message.content
            if not answer:
                raise ValueError("Empty response from LLM")
            return answer

        except RateLimitError as e:
            error_str = str(e)

            # Проверяем тип лимита
            is_free_limit = "free-models-per-day" in error_str

            # Если это free-limit ошибка - выбрасываем сразу, без retry
            if is_free_limit:
                error_msg = (
                    f"Rate limit exceeded: free-models-per-day. "
                    f"Add credits or wait until tomorrow (00:00 UTC). "
                    f"Error: {error_str[:150]}"
                )
                self.logger.error(error_msg)
                raise RateLimitExceededError(error_msg)

            # Для других типов лимитов используем retry с backoff
            for attempt in range(max_retries + 1):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,  # type: ignore[arg-type]
                    )
                    answer = response.choices[0].message.content
                    if not answer:
                        raise ValueError("Empty response from LLM")
                    return answer

                except RateLimitError as retry_error:
                    if attempt < max_retries:
                        delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                        self.logger.warning(
                            f"Rate limit hit (429). "
                            f"Retry {attempt + 1}/{max_retries} after {delay}s. "
                            f"Error: {str(retry_error)[:200]}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        error_msg = (
                            f"Rate limit exceeded after {max_retries} retries. "
                            f"Error: {str(retry_error)[:150]}"
                        )
                        self.logger.error(error_msg)
                        raise RateLimitExceededError(error_msg)

        except RateLimitExceededError:
            raise
        except Exception as e:
            self.logger.error(f"Error calling LLM API: {e}", exc_info=True)
            raise

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
            RateLimitExceededError: При превышении лимита (429)
            Exception: При других ошибках API
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

            answer = await self._api_call_with_retry(messages)
            self.logger.info(f"Received response from LLM: length={len(answer)}")
            return answer

        except RateLimitExceededError as e:
            self.logger.error(f"Rate limit in get_response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error in get_response: {e}", exc_info=True)
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
            RateLimitExceededError: При превышении лимита (429)
            Exception: При других ошибках API
        """
        try:
            # Добавляем сообщение пользователя в контекст
            await self.context_storage.add_message(user_id, "user", user_message)

            # Получаем историю для пользователя
            context = await self.context_storage.get_context(user_id)

            # Формируем запрос с системным промптом и историей
            messages = [
                {"role": "system", "content": self.system_prompt},
                *context,
            ]

            self.logger.info(
                f"Sending request to LLM with context: user_id={user_id}, "
                f"model={self.model}, context_length={len(context)}"
            )

            answer = await self._api_call_with_retry(messages)
            await self.context_storage.add_message(user_id, "assistant", answer)

            self.logger.info(f"Received response from LLM: user_id={user_id}, length={len(answer)}")
            return answer

        except RateLimitExceededError as e:
            self.logger.error(f"Rate limit in get_response_with_context: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Error calling LLM API with context for user_id={user_id}: {e}",
                exc_info=True,
            )
            raise

    async def reset_context(self, user_id: int) -> None:
        """
        Очистить контекст диалога для пользователя.

        Args:
            user_id: ID пользователя
        """
        await self.context_storage.reset_context(user_id)
