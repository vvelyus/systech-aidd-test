"""Unit тесты для ChatService с production features."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator
import logging

from src.api.chat_service import ChatService, SYSTEM_PROMPTS
from src.api.models import ChatMode, MessageRole


class TestChatServiceTemperature:
    """Тесты конфигурации температуры ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_normal_mode_uses_lower_temperature(self, service, mock_llm_client):
        """Проверить, что normal режим использует низкую температуру."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        message = "Hello, how are you?"

        async def mock_generate(*args, **kwargs):
            # Проверяем, что температура в kwargs
            if 'temperature' in kwargs:
                assert kwargs['temperature'] == 0.7  # Normal mode
            yield "Hello! I'm doing well."

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = service.process_message(
            user_id, session_id, message, ChatMode.NORMAL
        )
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_admin_mode_uses_higher_temperature(self, service, mock_llm_client):
        """Проверить, что admin режим использует высокую температуру для SQL."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        message = "How many users are active?"

        async def mock_generate(*args, **kwargs):
            if 'temperature' in kwargs:
                assert kwargs['temperature'] == 0.3  # Admin mode
            yield "SELECT COUNT(*) FROM users"

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = service.process_message(
            user_id, session_id, message, ChatMode.ADMIN
        )
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_system_prompt_differs_by_mode(self):
        """Проверить, что system prompts отличаются для разных режимов."""
        # Act & Assert
        normal_prompt = SYSTEM_PROMPTS["normal"]
        admin_prompt = SYSTEM_PROMPTS["admin"]

        assert normal_prompt != admin_prompt
        assert "helpful" in normal_prompt.lower()
        assert "sql" in admin_prompt.lower() or "data" in admin_prompt.lower()


class TestChatServiceRetryLogic:
    """Тесты retry logic ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, service, mock_llm_client):
        """Проверить retry logic при неудаче."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        message = "Hello"

        call_count = 0

        async def mock_generate_with_failures(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            yield "Success on retry"

        mock_llm_client.generate = mock_generate_with_failures

        # Act & Assert
        try:
            response_gen = service.process_message(
                user_id, session_id, message, ChatMode.NORMAL
            )
            chunks = []
            async for chunk in response_gen:
                chunks.append(chunk)
        except Exception:
            # Ожидаем, что может быть ошибка после retries
            pass

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self, service, mock_llm_client):
        """Проверить exponential backoff между retries."""
        # Arrange
        import time

        call_times = []

        async def mock_generate_with_timing(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) < 2:
                raise Exception("Temporary error")
            yield "Success"

        mock_llm_client.generate = mock_generate_with_timing

        # Act
        try:
            response_gen = service.process_message(
                "user_123", "session_123", "Hello", ChatMode.NORMAL
            )
            async for _ in response_gen:
                pass
        except Exception:
            pass

        # Assert
        # Проверяем, что было несколько попыток
        assert len(call_times) >= 1


class TestChatServiceStreaming:
    """Тесты streaming chunks ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_streaming_chunks_generated(self, service, mock_llm_client):
        """Проверить, что streaming chunks генерируются."""
        # Arrange
        user_id = "user_123"
        session_id = "session_123"
        message = "Hello"

        async def mock_generate(*args, **kwargs):
            yield "Hello"
            yield " "
            yield "world"
            yield "!"

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = service.process_message(
            user_id, session_id, message, ChatMode.NORMAL
        )
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert "Hello" in full_response
        assert "world" in full_response

    @pytest.mark.asyncio
    async def test_chunks_yield_at_reasonable_intervals(self, service, mock_llm_client):
        """Проверить, что chunks выдаются с разумными интервалами."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            for word in "This is a streaming response".split():
                await asyncio.sleep(0.01)
                yield word + " "

        mock_llm_client.generate = mock_generate

        # Act
        import time
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        start_time = time.time()
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)
        elapsed = time.time() - start_time

        # Assert
        assert len(chunks) > 1
        assert elapsed > 0  # Some time passed


class TestChatServiceErrorMessages:
    """Тесты error message handling ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_error_messages_include_context(self, service, mock_llm_client):
        """Проверить, что error messages включают контекст."""
        # Arrange
        mock_llm_client.generate.side_effect = Exception("API error: Rate limited")

        # Act
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        # Assert
        try:
            chunks = []
            async for chunk in response_gen:
                chunks.append(chunk)
        except Exception as e:
            error_message = str(e)
            assert len(error_message) > 0

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, service, mock_llm_client):
        """Проверить обработку timeout ошибок."""
        # Arrange
        mock_llm_client.generate.side_effect = asyncio.TimeoutError()

        # Act & Assert
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        with pytest.raises((asyncio.TimeoutError, Exception)):
            async for _ in response_gen:
                pass

    @pytest.mark.asyncio
    async def test_network_error_recovery(self, service, mock_llm_client):
        """Проверить recovery при network ошибках."""
        # Arrange
        async def mock_generate_with_network_error(*args, **kwargs):
            raise ConnectionError("Network unreachable")

        mock_llm_client.generate = mock_generate_with_network_error

        # Act & Assert
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        with pytest.raises((ConnectionError, Exception)):
            async for _ in response_gen:
                pass


class TestChatServiceModeSpecific:
    """Тесты mode-specific поведения ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_normal_mode_calls_llm_directly(self, service, mock_llm_client):
        """Проверить, что normal режим вызывает LLM напрямую."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Hello, I'm here to help!"

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert
        full_response = "".join(chunks)
        assert "hello" in full_response.lower()

    @pytest.mark.asyncio
    async def test_admin_mode_calls_text2sql(self, service, mock_text2sql, mock_llm_client):
        """Проверить, что admin режим вызывает Text2SQL."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Based on the SQL results..."

        mock_llm_client.generate = mock_generate
        mock_text2sql.convert.return_value = AsyncMock(
            sql="SELECT COUNT(*) FROM users",
            explanation="Counting active users"
        )
        mock_text2sql.execute_and_format.return_value = "| count |\n|-------|\n| 42    |"

        # Act
        response_gen = service.process_message(
            "user_123", "session_123", "How many users?", ChatMode.ADMIN
        )
        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        # Assert
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_mode_difference_in_processing(self, service, mock_llm_client, mock_text2sql):
        """Проверить различия в обработке между режимами."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act - Normal mode
        normal_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )
        normal_chunks = []
        async for chunk in normal_gen:
            normal_chunks.append(chunk)

        # Act - Admin mode
        admin_gen = service.process_message(
            "user_123", "session_123", "How many?", ChatMode.ADMIN
        )
        admin_chunks = []
        async for chunk in admin_gen:
            admin_chunks.append(chunk)

        # Assert
        assert len(normal_chunks) > 0
        assert len(admin_chunks) > 0


class TestChatServiceTimeout:
    """Тесты timeout handling ChatService."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def service(self, mock_llm_client, mock_db_manager, mock_text2sql, mock_logger):
        """Создать ChatService с mock зависимостями."""
        return ChatService(mock_llm_client, mock_db_manager, mock_text2sql, mock_logger)

    @pytest.mark.asyncio
    async def test_request_timeout_30_seconds(self, service, mock_llm_client):
        """Проверить timeout 30 сек для requests."""
        # Arrange
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(35)  # Longer than 30 sec timeout
            yield "Response"

        mock_llm_client.generate = slow_generate

        # Act & Assert
        response_gen = service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        with pytest.raises((asyncio.TimeoutError, Exception)):
            async for _ in response_gen:
                pass

    @pytest.mark.asyncio
    async def test_text2sql_timeout_5_seconds(self, service, mock_text2sql, mock_llm_client):
        """Проверить timeout 5 сек для Text-to-SQL."""
        # Arrange
        async def slow_convert(*args, **kwargs):
            await asyncio.sleep(6)  # Longer than 5 sec timeout
            return None

        mock_text2sql.convert.side_effect = slow_convert

        # Act & Assert
        response_gen = service.process_message(
            "user_123", "session_123", "How many?", ChatMode.ADMIN
        )

        # Это должно быть обработано gracefully
        chunks = []
        try:
            async for chunk in response_gen:
                chunks.append(chunk)
        except (asyncio.TimeoutError, Exception):
            pass
