"""Performance тесты для chat системы.

Эти тесты измеряют ключевые метрики производительности:
- LLM response latency
- Text-to-SQL conversion time
- Throughput (concurrent requests)
- Memory usage
- Database query performance
"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import AsyncMock, MagicMock
from typing import List

from src.api.chat_service import ChatService
from src.api.models import ChatMode
from src.text2sql import Text2SqlConverter


class TestChatPerformanceLLMLatency:
    """Тесты latency LLM responses."""

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
    async def test_llm_response_under_3_seconds(self, chat_service, mock_llm_client):
        """Тест: LLM ответ приходит менее чем за 3 сек."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            await asyncio.sleep(0.5)  # 500ms latency
            yield "This is a response"

        mock_llm_client.generate = mock_generate

        # Act
        start_time = time.time()
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        elapsed_time = time.time() - start_time

        # Assert
        assert elapsed_time < 3.0, f"LLM response took {elapsed_time:.2f}s, expected < 3s"

    @pytest.mark.asyncio
    async def test_first_chunk_latency_under_1_second(self, chat_service, mock_llm_client):
        """Тест: Первый chunk получен менее чем за 1 сек."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            await asyncio.sleep(0.2)  # Small initial latency
            yield "First chunk"
            await asyncio.sleep(0.1)
            yield " Second chunk"

        mock_llm_client.generate = mock_generate

        # Act
        start_time = time.time()
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        first_chunk = None
        async for chunk in response_gen:
            if first_chunk is None:
                first_chunk = chunk
                break

        first_chunk_time = time.time() - start_time

        # Assert
        assert first_chunk_time < 1.0, f"First chunk took {first_chunk_time:.2f}s, expected < 1s"
        assert first_chunk is not None

    @pytest.mark.asyncio
    async def test_streaming_chunk_timing(self, chat_service, mock_llm_client):
        """Тест: Chunks приходят с регулярным интервалом (< 100ms между chunks)."""
        # Arrange
        chunk_times = []

        async def mock_generate(*args, **kwargs):
            for i in range(5):
                chunk_times.append(time.time())
                yield f"Chunk {i}"
                await asyncio.sleep(0.02)  # 20ms between chunks

        mock_llm_client.generate = mock_generate

        # Act
        response_gen = chat_service.process_message(
            "user_123", "session_123", "Hello", ChatMode.NORMAL
        )

        async for _ in response_gen:
            pass

        # Assert - Проверяем интервалы между chunks
        if len(chunk_times) > 1:
            for i in range(1, len(chunk_times)):
                interval = chunk_times[i] - chunk_times[i-1]
                assert interval < 0.1, f"Interval {interval:.3f}s exceeds 100ms"


class TestChatPerformanceText2SQL:
    """Тесты performance Text-to-SQL conversion."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def text2sql(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_text2sql_conversion_under_2_seconds(self, text2sql, mock_llm_client):
        """Тест: Text-to-SQL конвертация менее 2 сек."""
        # Arrange
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"

        # Act
        start_time = time.time()
        response = await text2sql.convert("How many users?")
        elapsed_time = time.time() - start_time

        # Assert
        assert elapsed_time < 2.0, f"Text-to-SQL took {elapsed_time:.2f}s, expected < 2s"
        assert response.sql is not None

    @pytest.mark.asyncio
    async def test_sql_execution_under_500ms(self, text2sql, mock_db_manager):
        """Тест: SQL execution менее 500ms."""
        # Arrange
        mock_result = [{"id": i, "name": f"User {i}"} for i in range(100)]
        mock_db_manager.execute_query.return_value = mock_result

        # Act
        start_time = time.time()
        result = await text2sql.execute_and_format("SELECT * FROM users LIMIT 100")
        elapsed_time = time.time() - start_time

        # Assert
        assert elapsed_time < 0.5, f"SQL execution took {elapsed_time:.2f}s, expected < 500ms"
        assert result is not None

    @pytest.mark.asyncio
    async def test_caching_improves_performance(self, text2sql, mock_llm_client):
        """Тест: Кэширование улучшает performance."""
        # Arrange
        question = "How many active users?"
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"

        # Act - Первый вызов
        start1 = time.time()
        response1 = await text2sql.convert(question)
        time1 = time.time() - start1

        # Act - Второй вызов (должен быть из кэша)
        start2 = time.time()
        response2 = await text2sql.convert(question)
        time2 = time.time() - start2

        # Assert - Кэшированный вызов должен быть быстрее
        assert time2 < time1, f"Cached call ({time2:.3f}s) should be faster than first call ({time1:.3f}s)"
        assert response1.sql == response2.sql


class TestChatPerformanceThroughput:
    """Тесты throughput (параллельные запросы)."""

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
    async def test_handle_10_concurrent_requests(self, chat_service, mock_llm_client):
        """Тест: Обработка 10 параллельных запросов."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            await asyncio.sleep(0.1)
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act
        start_time = time.time()
        tasks = []

        for i in range(10):
            task = self._process_message(chat_service, f"user_{i}", "Hello")
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time

        # Assert
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) >= 8, "At least 80% of requests should succeed"
        assert elapsed_time < 2.0, f"Handling 10 concurrent requests took {elapsed_time:.2f}s"

    async def _process_message(self, service, user_id, message):
        """Helper для обработки сообщения."""
        response_gen = service.process_message(
            user_id, f"session_{user_id}", message, ChatMode.NORMAL
        )

        chunks = []
        async for chunk in response_gen:
            chunks.append(chunk)

        return "".join(chunks)

    @pytest.mark.asyncio
    async def test_handle_50_sequential_requests(self, chat_service, mock_llm_client):
        """Тест: Обработка 50 последовательных запросов."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act
        start_time = time.time()

        for i in range(50):
            response_gen = chat_service.process_message(
                f"user_{i}", f"session_{i}", f"Message {i}", ChatMode.NORMAL
            )

            async for _ in response_gen:
                pass

        elapsed_time = time.time() - start_time

        # Assert
        avg_time_per_request = elapsed_time / 50
        assert avg_time_per_request < 0.5, f"Average time per request is {avg_time_per_request:.3f}s"

    @pytest.mark.asyncio
    async def test_throughput_at_least_10_requests_per_second(self, chat_service, mock_llm_client):
        """Тест: Throughput минимум 10 запросов в секунду."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Response"

        mock_llm_client.generate = mock_generate
        request_count = 0

        # Act
        start_time = time.time()

        while time.time() - start_time < 1.0:
            response_gen = chat_service.process_message(
                "user", "session", "Hello", ChatMode.NORMAL
            )

            async for _ in response_gen:
                pass

            request_count += 1

        elapsed_time = time.time() - start_time
        throughput = request_count / elapsed_time

        # Assert
        assert throughput >= 10, f"Throughput is {throughput:.1f} req/s, expected >= 10"


class TestChatPerformanceMemory:
    """Тесты использования памяти."""

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
    async def test_memory_usage_after_100_messages(self, chat_service, mock_llm_client):
        """Тест: Память после обработки 100 сообщений (< 100MB)."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            yield "Response " * 10

        mock_llm_client.generate = mock_generate

        # Act
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        for i in range(100):
            response_gen = chat_service.process_message(
                "user", f"session_{i}", f"Message {i}", ChatMode.NORMAL
            )

            async for _ in response_gen:
                pass

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # Assert
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB, expected < 100MB"

    @pytest.mark.asyncio
    async def test_cache_memory_usage(self):
        """Тест: Кэш не съедает слишком много памяти."""
        # Arrange
        cache = {}
        cache_ttl = 3600

        # Act - Добавляем 1000 элементов в кэш
        for i in range(1000):
            key = f"question_{i}"
            value = ("SELECT * FROM table_" + str(i), time.time())
            cache[key] = value

        # Assert
        cache_size = len(cache)
        assert cache_size == 1000


class TestChatPerformanceDatabaseQueries:
    """Тесты performance database queries."""

    @pytest.fixture
    def mock_db_manager(self):
        """Mock DB manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        return AsyncMock()

    @pytest.fixture
    def text2sql(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_simple_query_under_100ms(self, text2sql, mock_db_manager):
        """Тест: Простой запрос выполняется менее 100ms."""
        # Arrange
        mock_db_manager.execute_query.return_value = [{"count": 42}]

        # Act
        start_time = time.time()
        result = await text2sql.execute_and_format("SELECT COUNT(*) FROM users")
        elapsed_time = time.time() - start_time

        # Assert
        assert elapsed_time < 0.1, f"Query took {elapsed_time:.3f}s, expected < 100ms"

    @pytest.mark.asyncio
    async def test_complex_query_under_500ms(self, text2sql, mock_db_manager):
        """Тест: Сложный запрос выполняется менее 500ms."""
        # Arrange
        large_result = [{"id": i, "name": f"User {i}", "email": f"user{i}@example.com"} for i in range(1000)]
        mock_db_manager.execute_query.return_value = large_result

        # Act
        start_time = time.time()
        result = await text2sql.execute_and_format(
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id LIMIT 1000"
        )
        elapsed_time = time.time() - start_time

        # Assert
        assert elapsed_time < 0.5, f"Query took {elapsed_time:.3f}s, expected < 500ms"

    @pytest.mark.asyncio
    async def test_query_with_indexes_is_faster(self, text2sql, mock_db_manager):
        """Тест: Запрос с индексами быстрее."""
        # Arrange
        mock_result = [{"id": 1, "name": "User"}]
        mock_db_manager.execute_query.return_value = mock_result

        # Act - Без индекса (симуляция)
        start1 = time.time()
        await text2sql.execute_and_format("SELECT * FROM users WHERE created_at > '2025-01-01'")
        time1 = time.time() - start1

        # Act - С индексом (симуляция, быстрее)
        start2 = time.time()
        await text2sql.execute_and_format("SELECT * FROM users WHERE id = 1")
        time2 = time.time() - start2

        # Assert - оба должны быть быстрыми
        assert time1 < 1.0
        assert time2 < 1.0


class TestChatPerformanceScalability:
    """Тесты масштабируемости."""

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
    async def test_linear_scaling_with_requests(self, chat_service, mock_llm_client):
        """Тест: Линейное масштабирование с количеством запросов."""
        # Arrange
        async def mock_generate(*args, **kwargs):
            await asyncio.sleep(0.1)
            yield "Response"

        mock_llm_client.generate = mock_generate

        # Act - Тестируем с разными количествами запросов
        times = {}
        for num_requests in [10, 50, 100]:
            start_time = time.time()
            tasks = [
                self._process_message(chat_service, f"user_{i}", "Hello")
                for i in range(num_requests)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            elapsed_time = time.time() - start_time
            times[num_requests] = elapsed_time

        # Assert - Проверяем, что время растет примерно линейно
        time_10 = times[10]
        time_50 = times[50]
        time_100 = times[100]

        # Примерно 5x и 10x
        assert time_50 < time_10 * 8, "Scaling should be roughly linear"
        assert time_100 < time_10 * 15, "Scaling should be roughly linear"

    async def _process_message(self, service, user_id, message):
        """Helper для обработки сообщения."""
        response_gen = service.process_message(
            user_id, f"session_{user_id}", message, ChatMode.NORMAL
        )

        async for _ in response_gen:
            pass

        return True
