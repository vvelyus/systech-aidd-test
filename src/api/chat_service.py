"""Сервис для обработки чат-сообщений с поддержкой streaming."""

import asyncio
import logging
import time
import uuid
from typing import TYPE_CHECKING, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import ChatMode, ChatMessage as ChatMessageModel, MessageRole
from src.models import ChatMessage as ChatMessageDB, ChatSession as ChatSessionDB
from src.text2sql import Text2SqlConverter
from src.llm_client import RateLimitExceededError

if TYPE_CHECKING:
    from src.llm_client import LLMClient
    from src.database import DatabaseManager


# Специализированные system prompts для разных режимов
SYSTEM_PROMPTS = {
    "normal": """You are a helpful AI assistant. Your role is to:
1. Answer questions accurately and comprehensively
2. Provide context-aware responses based on conversation history
3. Ask clarifying questions if needed
4. Be concise but informative
5. Maintain conversation context across multiple messages

Be friendly and professional in your responses.""",

    "admin": """You are a SQL expert and data analyst assistant. Your role is to:
1. Analyze dialog statistics from the database
2. Provide insights based on SQL query results
3. Answer questions about user engagement, message patterns, and trends
4. Format results clearly and concisely
5. Suggest relevant follow-up queries

Be precise and fact-based in your responses."""
}


class ChatService:
    """Сервис для обработки сообщений чата в обоих режимах."""

    def __init__(
        self,
        llm_client: "LLMClient",
        db_manager: "DatabaseManager",
        logger: logging.Logger,
        chunk_size: int = 50,
        request_timeout: float = 30.0,
        text2sql_timeout: float = 5.0,
    ) -> None:
        """
        Инициализация сервиса.

        Args:
            llm_client: Клиент для LLM
            db_manager: Менеджер базы данных
            logger: Логгер
            chunk_size: Размер chunk'а для streaming (количество символов)
            request_timeout: Таймаут для LLM request в секундах (default 30s)
            text2sql_timeout: Таймаут для Text-to-SQL в секундах (default 5s)
        """
        self.llm_client = llm_client
        self.db_manager = db_manager
        self.logger = logger
        self.text2sql = Text2SqlConverter(llm_client, db_manager, logger)
        self.chunk_size = chunk_size
        self.request_timeout = request_timeout
        self.text2sql_timeout = text2sql_timeout

        # Temperature config per mode
        self.temperature_config = {
            ChatMode.NORMAL: 0.7,  # Higher for more conversational, creative responses
            ChatMode.ADMIN: 0.3,   # Lower for more factual, deterministic SQL responses
        }

        self.logger.info(
            f"ChatService initialized with timeouts: "
            f"request={request_timeout}s, text2sql={text2sql_timeout}s"
        )

    async def process_message(
        self,
        message: str,
        session_id: str,
        mode: ChatMode = ChatMode.NORMAL,
        context_storage=None,
        max_retries: int = 3,
    ) -> AsyncGenerator[str, None]:
        """
        Обрабатывает сообщение пользователя и возвращает streaming ответ.

        Args:
            message: Сообщение от пользователя
            session_id: ID сессии чата
            mode: Режим чата (normal или admin)
            context_storage: Хранилище контекста для обычного режима
            max_retries: Максимальное количество попыток при ошибке

        Yields:
            Части ответа ассистента
        """
        # Сохраняем сообщение пользователя
        user_msg_id = str(uuid.uuid4())
        user_message = ChatMessageDB(
            id=user_msg_id,
            user_session_id=session_id,
            content=message,
            role=MessageRole.USER.value,
            mode=mode.value,
        )
        await self.save_message(user_message)

        try:
            if mode == ChatMode.ADMIN:
                # Админ режим: Text-to-SQL pipeline с retry logic
                async for chunk in self._process_admin_mode_with_retry(
                    message, session_id, max_retries
                ):
                    yield chunk
            else:
                # Обычный режим: LLM ассистент с retry logic
                async for chunk in self._process_normal_mode_with_retry(
                    message, session_id, context_storage, max_retries
                ):
                    yield chunk

        except RateLimitExceededError as e:
            # Специальная обработка для rate limit ошибок
            self.logger.error(f"Rate limit in chat service: {e}")

            # Формируем дружественное сообщение на русском
            error_message = (
                "Лимит бесплатного плана исчерпан\n"
                "Дневной лимит на бесплатное использование достигнут.\n\n"
                "Что делать:\n"
                "1. Добавьте кредиты на https://openrouter.ai/account/billing\n"
                "2. Дождитесь завтра (00:00 UTC) - лимит сбросится автоматически\n"
                "3. Используйте более простые запросы\n\n"
                "Почему так происходит: Бесплатный план ограничен примерно 30-50 запросами в день. Перейдите на платный план для неограниченного использования."
            )
            yield error_message

            # Save error message to history
            error_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                user_session_id=session_id,
                content=error_message,
                role=MessageRole.ASSISTANT.value,
                mode=mode.value,
            )
            await self.save_message(error_msg)

        except Exception as e:
            self.logger.error(f"Error processing message in {mode.value} mode: {e}")
            error_message = (
                f"Error processing your request: {str(e)[:100]}. "
                "Please try again with a simpler question."
            )
            yield error_message

            # Save error message to history
            error_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                user_session_id=session_id,
                content=error_message,
                role=MessageRole.ASSISTANT.value,
                mode=mode.value,
            )
            await self.save_message(error_msg)

    async def _process_normal_mode_with_retry(
        self,
        message: str,
        session_id: str,
        context_storage,
        max_retries: int,
    ) -> AsyncGenerator[str, None]:
        """Process normal mode with retry logic."""
        for attempt in range(max_retries):
            try:
                async for chunk in self._process_normal_mode(
                    message, session_id, context_storage
                ):
                    yield chunk
                return
            except RateLimitExceededError:
                # Don't retry for rate limits, just raise immediately
                self.logger.error(f"Rate limit error - no retry for rate limits")
                raise
            except asyncio.TimeoutError:
                self.logger.warning(f"Normal mode timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                raise
            except Exception as e:
                self.logger.error(f"Normal mode error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise

    async def _process_admin_mode_with_retry(
        self,
        message: str,
        session_id: str,
        max_retries: int,
    ) -> AsyncGenerator[str, None]:
        """Process admin mode with retry logic."""
        for attempt in range(max_retries):
            try:
                async for chunk in self._process_admin_mode(message, session_id):
                    yield chunk
                return
            except RateLimitExceededError:
                # Don't retry for rate limits, just raise immediately
                self.logger.error(f"Rate limit error - no retry for rate limits")
                raise
            except asyncio.TimeoutError:
                self.logger.warning(f"Admin mode timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                raise
            except Exception as e:
                self.logger.error(f"Admin mode error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise

    def _optimize_streaming_chunks(self, text: str) -> list[str]:
        """
        Оптимизировать chunks для streaming.

        Выбрать точки разбиения:
        - После каждых ~chunk_size символов
        - На границах предложений (. ! ? ;)
        - После запятых и двоеточий для естественного разбиения
        """
        chunks = []
        current_chunk = ""

        for i, char in enumerate(text):
            current_chunk += char

            # Check if we should split
            should_split = False
            if len(current_chunk) >= self.chunk_size:
                # Look for natural break points
                if char in ".!?;":
                    should_split = True
                elif char == "," and len(current_chunk) >= self.chunk_size * 0.8:
                    should_split = True
                elif i == len(text) - 1:  # Last character
                    should_split = True
            elif i == len(text) - 1:  # Last character
                should_split = True

            if should_split and current_chunk.strip():
                chunks.append(current_chunk)
                current_chunk = ""

        return chunks if chunks else [text]

    async def _process_normal_mode(
        self,
        message: str,
        session_id: str,
        context_storage=None,
    ) -> AsyncGenerator[str, None]:
        """
        Обработать сообщение в обычном режиме (LLM assistant).

        Загружает историю сообщений из БД и передает контекст в LLM,
        чтобы бот помнил предыдущие разговоры.
        """
        # Добавить специализированный system prompt для normal режима
        system_prompt = SYSTEM_PROMPTS["normal"]
        temperature = self.temperature_config[ChatMode.NORMAL]

        # Get response from LLM with timeout
        try:
            # 👇 НОВОЕ: Загружаем историю сообщений из БД для этой сессии
            history = await self.get_history(session_id, limit=20)

            # Формируем messages для LLM с историей
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Добавляем предыдущие сообщения из истории
            for hist_msg in history:
                messages.append({
                    "role": hist_msg.role,
                    "content": hist_msg.content
                })

            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": message
            })

            self.logger.info(
                f"Processing message in normal mode with {len(history)} history messages. "
                f"Session: {session_id}"
            )

            # Вызываем LLM с полным контекстом (напрямую, не через context_storage)
            full_response = ""
            response = await asyncio.wait_for(
                self._call_llm_with_messages(messages),
                timeout=self.request_timeout
            )

            # Оптимизировать chunks для streaming
            chunks = self._optimize_streaming_chunks(response)

            for chunk in chunks:
                full_response += chunk
                yield chunk

            # Сохранить ответ в БД
            assistant_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                user_session_id=session_id,
                content=full_response,
                role=MessageRole.ASSISTANT.value,
                mode=ChatMode.NORMAL.value,
            )
            await self.save_message(assistant_msg)

        except asyncio.TimeoutError:
            self.logger.error(f"LLM timeout after {self.request_timeout}s")
            yield f"Sorry, the response took too long ({self.request_timeout}s). Please try with a simpler question."

    async def _call_llm_with_messages(self, messages: list[dict]) -> str:
        """
        Вызвать LLM напрямую с массивом messages.

        Args:
            messages: Массив сообщений в формате [{"role": "...", "content": "..."}, ...]

        Returns:
            Ответ от LLM
        """
        try:
            response = await self.llm_client._api_call_with_retry(messages)
            return response
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            raise

    async def _process_admin_mode(
        self,
        message: str,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        Обработать сообщение в админ режиме (Text-to-SQL + LLM).
        """
        system_prompt = SYSTEM_PROMPTS["admin"]
        temperature = self.temperature_config[ChatMode.ADMIN]

        try:
            # Этап 1: Text-to-SQL конвертация с timeout
            text2sql_response = await asyncio.wait_for(
                self.text2sql.convert(message, max_retries=3),
                timeout=self.text2sql_timeout
            )

            if not text2sql_response.sql:
                error_msg = (
                    f"Could not generate SQL: {text2sql_response.error or 'Unknown error'}. "
                    "Please try with a different question."
                )
                yield error_msg
                return

            # Yield the SQL query for debugging
            yield f"SQL Query: {text2sql_response.sql}\n\n"

            # Этап 2: Выполнить SQL и получить результаты
            results = await asyncio.wait_for(
                self.text2sql.execute_and_format(
                    text2sql_response.sql,
                    max_rows=1000,
                    timeout=10.0
                ),
                timeout=20.0
            )

            # Этап 3: Отправить результаты в LLM для интерпретации
            llm_prompt = f"""Based on the following SQL query results, provide a concise analysis and answer the user's question.

SQL Query: {text2sql_response.sql}

Results:
{results}

User Question: {message}

Provide a clear, factual answer based on the data."""

            full_response = ""
            llm_response = await asyncio.wait_for(
                self.llm_client.get_response(llm_prompt),
                timeout=self.request_timeout
            )

            # Оптимизировать chunks для streaming
            chunks = self._optimize_streaming_chunks(llm_response)

            for chunk in chunks:
                full_response += chunk
                yield chunk

            # Сохранить полный ответ в БД (с SQL запросом)
            assistant_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                user_session_id=session_id,
                content=full_response,
                role=MessageRole.ASSISTANT.value,
                mode=ChatMode.ADMIN.value,
                sql_query=text2sql_response.sql,  # Save SQL for debugging
            )
            await self.save_message(assistant_msg)

        except asyncio.TimeoutError as e:
            error_msg = (
                f"Request timed out (too complex query). "
                "Please try with a simpler question."
            )
            yield error_msg
        except Exception as e:
            self.logger.error(f"Error in admin mode: {e}")
            yield f"Error processing your request: {str(e)[:100]}"

    async def save_message(self, message: ChatMessageDB) -> None:
        """
        Сохраняет сообщение в БД.

        Args:
            message: Сообщение для сохранения
        """
        try:
            session = self.db_manager.create_session()
            session.add(message)
            await session.commit()
            self.logger.debug(f"Message saved: {message.id}")
        except Exception as e:
            self.logger.error(f"Error saving message: {e}")
            raise

    async def get_history(
        self, session_id: str, limit: int = 50
    ) -> list[ChatMessageModel]:
        """
        Получает историю сообщений для сессии.

        Args:
            session_id: ID сессии
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений из БД
        """
        try:
            session = self.db_manager.create_session()
            stmt = (
                select(ChatMessageDB)
                .where(ChatMessageDB.user_session_id == session_id)
                .order_by(ChatMessageDB.created_at.asc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            messages = result.scalars().all()

            # Конвертируем в Pydantic модели
            return [
                ChatMessageModel(
                    id=msg.id,
                    user_session_id=msg.user_session_id,
                    content=msg.content,
                    role=msg.role,
                    mode=msg.mode,
                    sql_query=msg.sql_query,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in messages
            ]

        except Exception as e:
            self.logger.error(f"Error getting history: {e}")
            return []

    async def create_session(
        self, user_id: int, mode: ChatMode = ChatMode.NORMAL
    ) -> str:
        """
        Создает новую сессию чата.

        Args:
            user_id: ID пользователя
            mode: Режим чата

        Returns:
            ID новой сессии
        """
        try:
            session_id = str(uuid.uuid4())
            session = ChatSessionDB(
                id=session_id,
                user_id=user_id,
                mode=mode.value,
            )

            db_session = self.db_manager.create_session()
            db_session.add(session)
            await db_session.commit()
            self.logger.info(f"Chat session created: {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            raise

    async def get_session(self, session_id: str) -> ChatSessionDB | None:
        """
        Получает информацию о сессии.

        Args:
            session_id: ID сессии

        Returns:
            Объект сессии или None
        """
        try:
            db_session = self.db_manager.create_session()
            stmt = select(ChatSessionDB).where(ChatSessionDB.id == session_id)
            result = await db_session.execute(stmt)
            return result.scalars().first()

        except Exception as e:
            self.logger.error(f"Error getting session: {e}")
            return None
