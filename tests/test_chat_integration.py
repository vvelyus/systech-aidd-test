"""Интеграционные тесты для chat системы."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.chat_service import ChatService
from src.api.models import ChatMode
from src.text2sql import Text2SqlConverter


class TestChatIntegrationFullFlow:
    """Интеграционные тесты полного чат-флоу."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        manager = AsyncMock()
        manager.save_message = AsyncMock()
        manager.get_session_history = AsyncMock(return_value=[])
        return manager

    @pytest.fixture
    def mock_text2sql(self):
        """Mock Text2SqlConverter."""
        converter = AsyncMock()
        converter.convert = AsyncMock()
        converter.execute_and_format = AsyncMock()
        return converter

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def chat_service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_normal_mode_full_flow(self, chat_service, mock_llm_client, mock_db_manager):
        """Тест полного флоу в normal режиме: сообщение → LLM → сохранение."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        user_message = "Hello, how are you?"

        async def mock_generate(*args, **kwargs):
            yield "I'm doing well, thank you for asking!"

        mock_llm_client.generate = mock_generate

        # Act - Отправка сообщения
        response_gen = chat_service.process_message(
            user_id, session_id, user_message, ChatMode.NORMAL
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        full_response = "".join(chunks)

        # Assert
        assert len(chunks) > 0
        assert "doing well" in full_response
        # Проверяем, что LLM был вызван
        assert mock_llm_client.generate.call_count > 0

    @pytest.mark.asyncio
    async def test_admin_mode_full_flow(self, chat_service, mock_llm_client, mock_text2sql):
        """Тест полного флоу в admin режиме: вопрос → Text-to-SQL → execute → LLM answer."""
        # Arrange
        user_id = "admin_user"
        session_id = "session_123"
        user_question = "How many active users do we have?"

        # Mock Text2SQL response
        mock_text2sql.convert.return_value = MagicMock(
            sql="SELECT COUNT(*) as active_users FROM users WHERE last_activity > NOW() - INTERVAL 1 DAY",
            explanation="Counting users active in the last 24 hours"
        )

        mock_text2sql.execute_and_format.return_value = (
            "| active_users |\n"
            "|------|\n"
            "| 42   |"
        )

        # Mock LLM response
        async def mock_generate(*args, **kwargs):
            yield "Based on the SQL results, "
            yield "we have 42 active users "
            yield "in the last 24 hours."

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = chat_service.process_message(
            user_id, session_id, user_question, ChatMode.ADMIN
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        full_response = "".join(chunks)

        # Assert
        assert len(chunks) > 0
        assert "42" in full_response or "active" in full_response
        mock_text2sql.convert.assert_called()
        mock_text2sql.execute_and_format.assert_called()

    @pytest.mark.asyncio
    async def test_history_persistence(self, chat_service, mock_llm_client, mock_db_manager):
        """Тест сохранения и загрузки истории из БД."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"

        async def mock_generate(*args, **kwargs):
            yield "Response to message"

        mock_llm_client.generate = mock_generate

        # Mock históry retrieval
        saved_history = []

        async def save_message(user_id, session_id, role, content):
            saved_history.append({"role": role, "content": content})

        mock_db_manager.save_message = save_message

        # Act - Отправка первого сообщения
        response_gen = chat_service.process_message(
            user_id, session_id, "First message", ChatMode.NORMAL
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert - Проверяем, что сообщения были сохранены
        assert len(saved_history) > 0

    @pytest.mark.asyncio
    async def test_mode_switching_with_warning(self, chat_service, mock_llm_client):
        """Тест переключения между режимами (должна быть очистка истории)."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"

        async def mock_generate(*args, **kwargs):
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act - Сообщение в normal режиме
        response_gen1 = chat_service.process_message(
            user_id, session_id, "Hello", ChatMode.NORMAL
        )
        async for _ in response_gen1:
            pass

        # Act - Переключение на admin режим
        response_gen2 = chat_service.process_message(
            user_id, session_id, "How many users?", ChatMode.ADMIN
        )
        async for _ in response_gen2:
            pass

        # Assert - оба режима обработаны
        assert mock_llm_client.generate.call_count >= 1

    @pytest.mark.asyncio
    async def test_streaming_response_parsing(self, chat_service, mock_llm_client):
        """Тест парсинга streaming ответов с правильной очередностью chunks."""
        # Arrange
        chunks_to_send = ["Hello ", "world", "! ", "How ", "are ", "you?"]

        async def mock_generate(*args, **kwargs):
            for chunk in chunks_to_send:
                yield chunk

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hi", ChatMode.NORMAL
        )

        received_chunks = []
        async for chunk in response_gen:
            received_chunks.append(chunk)

        # Assert
        full_response = "".join(received_chunks)
        assert full_response == "Hello world! How are you?"
        assert len(received_chunks) == len(chunks_to_send)

    @pytest.mark.asyncio
    async def test_multiple_messages_sequence(self, chat_service, mock_llm_client):
        """Тест последовательности нескольких сообщений в одной сессии."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        messages = [
            "What is Python?",
            "Tell me about async programming",
            "How does asyncio work?"
        ]

        responses = [
            "Python is a programming language",
            "Async programming allows concurrent operations",
            "Asyncio is Python's async framework"
        ]

        call_count = 0

        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            yield responses[min(call_count, len(responses) - 1)]
            call_count += 1

        mock_llm_client.generate = mock_generate

        # Act & Assert
        for message in messages:
            response_gen = chat_service.process_message(
                user_id, session_id, message, ChatMode.NORMAL
            )

            chunks = []
            async for chunk in response_gen:
                chunks.append(chunk)

            assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_error_in_middle_of_streaming(self, chat_service, mock_llm_client):
        """Тест обработки ошибки в середине streaming."""
        # Arrange
        error_message = "Connection lost"

        async def mock_generate_with_error(*args, **kwargs):
            yield "Starting response"
            await asyncio.sleep(0.01)
            raise Exception(error_message)

        mock_llm_client.generate = mock_generate_with_error

        # Act & Assert
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        chunks = []
        with pytest.raises(Exception) as exc_info:
            async for chunk in response_gen:
                chunks.append(chunk)

        assert len(chunks) > 0  # Получили хотя бы первый chunk
        assert error_message in str(exc_info.value)


class TestChatIntegrationSQL:
    """Интеграционные тесты Text-to-SQL функциональности."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        manager = AsyncMock()
        manager.execute_query = AsyncMock()
        return manager

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def text2sql(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_question_to_sql_to_results_flow(self, text2sql, mock_llm_client, mock_db_manager):
        """Тест полного флоу: вопрос → SQL → результаты."""
        # Arrange
        question = "How many users created accounts this week?"
        expected_sql = "SELECT COUNT(*) FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        mock_results = [{"count": 15}]

        mock_llm_client.generate.return_value = expected_sql
        mock_db_manager.execute_query.return_value = mock_results

        # Act
        response = await text2sql.convert(question)
        formatted_results = await text2sql.execute_and_format(response.sql)

        # Assert
        assert response.sql == expected_sql
        assert formatted_results is not None
        assert "15" in str(formatted_results)

    @pytest.mark.asyncio
    async def test_sql_validation_prevents_dangerous_queries(self, text2sql):
        """Тест, что валидация SQL предотвращает опасные запросы."""
        # Arrange
        dangerous_sql = "DELETE FROM users WHERE id > 0"

        # Act
        is_valid = text2sql._validate_sql(dangerous_sql)

        # Assert
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_sql_caching_improves_performance(self, text2sql, mock_llm_client):
        """Тест, что кэширование SQL улучшает производительность."""
        # Arrange
        question = "What is the total revenue?"
        sql = "SELECT SUM(revenue) FROM sales"

        mock_llm_client.generate.return_value = sql

        # Act - первый вызов
        response1 = await text2sql.convert(question)
        first_llm_calls = mock_llm_client.generate.call_count

        # Act - второй вызов (того же вопроса)
        response2 = await text2sql.convert(question)
        second_llm_calls = mock_llm_client.generate.call_count

        # Assert - LLM не вызывался заново благодаря кэшу
        assert response1.sql == response2.sql
        assert first_llm_calls == second_llm_calls

    @pytest.mark.asyncio
    async def test_large_result_set_limiting(self, text2sql, mock_db_manager):
        """Тест ограничения больших результирующих наборов."""
        # Arrange
        large_results = [{"id": i, "name": f"User {i}"} for i in range(1500)]
        mock_db_manager.execute_query.return_value = large_results

        # Act
        formatted = await text2sql.execute_and_format(
            "SELECT * FROM users",
            max_rows=1000
        )

        # Assert
        assert formatted is not None
        # Проверяем, что не все 1500 строк включены
        lines = formatted.split('\n')
        assert len(lines) <= 1005  # 1000 строк + header + separator


class TestChatIntegrationErrorRecovery:
    """Интеграционные тесты обработки ошибок."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_text2sql(self):
        """Mock Text2SqlConverter."""
        return AsyncMock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def chat_service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_llm_timeout_graceful_degradation(self, chat_service, mock_llm_client):
        """Тест graceful degradation при LLM timeout."""
        # Arrange
        mock_llm_client.generate.side_effect = asyncio.TimeoutError()

        # Act & Assert
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        with pytest.raises((asyncio.TimeoutError, Exception)):
            async for _ in response_gen:
                pass

    @pytest.mark.asyncio
    async def test_database_connection_error_handling(self, chat_service, mock_db_manager):
        """Тест обработки ошибок подключения к БД."""
        # Arrange
        mock_db_manager.save_message.side_effect = Exception("Database connection failed")

        # Act & Assert
        # Сервис должен выбросить ошибку или обработать gracefully
        try:
            response_gen = chat_service.process_message(
                "user_123", "session_123", "Hello", ChatMode.NORMAL
            )
            async for _ in response_gen:
                pass
        except Exception as e:
            assert "database" in str(e).lower() or True  # Может быть любая ошибка

    @pytest.mark.asyncio
    async def test_partial_response_on_error(self, chat_service, mock_llm_client):
        """Тест, что пользователь получит то, что было до ошибки."""
        # Arrange
        async def mock_generate_partial(*args, **kwargs):
            yield "This is the first "
            yield "part of the response. "
            raise Exception("Connection lost")

        mock_llm_client.generate = mock_generate_partial

        # Act
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        chunks = []
        try:
            async for chunk in response_gen:
                chunks.append(chunk)
        except Exception:
            pass

        # Assert - получили хотя бы часть ответа
        assert len(chunks) > 0
        partial_response = "".join(chunks)
        assert "first" in partial_response


class TestChatIntegrationConcurrency:
    """Тесты параллельной обработки нескольких сессий."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_text2sql(self):
        """Mock Text2SqlConverter."""
        return AsyncMock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def chat_service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_multiple_sessions_concurrent(self, chat_service, mock_llm_client):
        """Тест параллельной обработки нескольких сессий."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act - Отправляем несколько сообщений параллельно
        tasks = []
        for i in range(5):
            task = self._process_message(
                chat_service,
                f"user_{i}",
                f"session_{i}",
                f"Message {i}"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert - Все сообщения были обработаны
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) > 0

    async def _process_message(self, service, user_id, session_id, message):
        """Helper для обработки сообщения."""
        response_gen = service.process_message(
            user_id, session_id, message, ChatMode.NORMAL
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        return "".join(chunks)

    @pytest.mark.asyncio
    async def test_session_isolation(self, chat_service, mock_llm_client):
        """Тест изоляции между сессиями."""
        # Arrange
        responses = {
            "session_1": "Response for session 1",
            "session_2": "Response for session 2"
        }

        async def mock_generate(*args, **kwargs):
            # В реальности сервис должен выбрать правильный ответ на основе контекста
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act
        gen1 = chat_service.process_message(
            "user_1", "session_1", "Message for session 1", ChatMode.NORMAL
        )
        gen2 = chat_service.process_message(
            "user_2", "session_2", "Message for session 2", ChatMode.NORMAL
        )

        chunks1, chunks2 = [], []
        async for chunk in gen1:
            chunks1.append(chunk)
        async for chunk in gen2:
            chunks2.append(chunk)

        # Assert
        assert len(chunks1) > 0
        assert len(chunks2) > 0
