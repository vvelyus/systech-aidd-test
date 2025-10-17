"""Unit тесты для Text2SqlConverter с production features."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import logging

from src.text2sql import Text2SqlConverter
from src.api.models import TextToSqlResponse


class TestText2SqlValidation:
    """Тесты валидации SQL в Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_allowed_keywords_passed(self, converter):
        """Проверить, что разрешенные SQL keywords пропускаются."""
        # Arrange
        valid_sql = "SELECT id, name FROM users WHERE id > 10 ORDER BY name LIMIT 100"

        # Act
        is_valid = converter._validate_sql(valid_sql)

        # Assert
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_forbidden_keywords_rejected(self, converter):
        """Проверить, что запрещенные SQL keywords отклоняются."""
        forbidden_queries = [
            "DELETE FROM users WHERE id = 1",
            "DROP TABLE users",
            "INSERT INTO users VALUES (1, 'test')",
            "UPDATE users SET name = 'new' WHERE id = 1",
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
            "TRUNCATE TABLE users"
        ]

        for sql in forbidden_queries:
            is_valid = converter._validate_sql(sql)
            assert is_valid is False, f"SQL должен быть отклонен: {sql}"

    @pytest.mark.asyncio
    async def test_empty_sql_rejected(self, converter):
        """Проверить, что пустой SQL отклоняется."""
        is_valid = converter._validate_sql("")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_malformed_sql_rejected(self, converter):
        """Проверить, что некорректный SQL отклоняется."""
        malformed_queries = [
            "SELECT * FROM WHERE id = 1",  # Missing table
            "SELECT FROM users",  # Missing columns
            "SELECTT * FROM users",  # Typo
        ]

        for sql in malformed_queries:
            is_valid = converter._validate_sql(sql)
            assert is_valid is False, f"SQL должен быть отклонен: {sql}"


class TestText2SqlCaching:
    """Тесты кэширования Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger, cache_ttl=3600)

    @pytest.mark.asyncio
    async def test_same_question_returns_cached_result(self, converter, mock_llm_client):
        """Проверить, что одинаковые вопросы возвращают закэшированный результат."""
        # Arrange
        question = "How many users are active?"
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"

        # Act - первый запрос
        response1 = await converter.convert(question)
        first_call_count = mock_llm_client.generate.call_count

        # Act - второй запрос (того же вопроса)
        response2 = await converter.convert(question)
        second_call_count = mock_llm_client.generate.call_count

        # Assert
        assert response1.sql == response2.sql
        assert first_call_count == second_call_count, "LLM не должен вызываться для закэшированного вопроса"

    @pytest.mark.asyncio
    async def test_different_questions_call_llm(self, converter, mock_llm_client):
        """Проверить, что разные вопросы вызывают LLM."""
        # Arrange
        question1 = "How many users are active?"
        question2 = "What is the average message length?"
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"

        # Act
        await converter.convert(question1)
        call_count_1 = mock_llm_client.generate.call_count

        await converter.convert(question2)
        call_count_2 = mock_llm_client.generate.call_count

        # Assert
        assert call_count_2 > call_count_1, "LLM должен вызваться для нового вопроса"

    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self, converter, mock_llm_client):
        """Проверить, что кэш истекает после TTL."""
        # Arrange
        question = "How many users are active?"
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"
        converter.cache_ttl = 1  # 1 секунда

        # Act
        await converter.convert(question)
        initial_calls = mock_llm_client.generate.call_count

        # Ждем истечения TTL
        await asyncio.sleep(1.1)

        # Запрашиваем снова
        await converter.convert(question)
        final_calls = mock_llm_client.generate.call_count

        # Assert
        assert final_calls > initial_calls, "LLM должен быть вызван после истечения TTL"


class TestText2SqlTimeout:
    """Тесты timeout обработки Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_sql_execution_timeout(self, converter, mock_db_manager):
        """Проверить, что SQL execution с timeout > 5 сек обрабатывается."""
        # Arrange
        sql = "SELECT * FROM users WHERE id = 1"

        async def slow_query(*args, **kwargs):
            await asyncio.sleep(6)  # Longer than 5 sec timeout
            return None

        mock_db_manager.execute_query.side_effect = slow_query

        # Act & Assert
        with pytest.raises((asyncio.TimeoutError, Exception)):
            await converter.execute_and_format(sql, timeout=5)

    @pytest.mark.asyncio
    async def test_sql_execution_within_timeout(self, converter, mock_db_manager):
        """Проверить, что SQL execution в пределах timeout работает."""
        # Arrange
        sql = "SELECT * FROM users LIMIT 10"
        mock_result = [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]

        async def quick_query(*args, **kwargs):
            await asyncio.sleep(0.1)  # Within 5 sec timeout
            return mock_result

        mock_db_manager.execute_query.side_effect = quick_query

        # Act
        result = await converter.execute_and_format(sql, timeout=5)

        # Assert
        assert result is not None
        assert "User 1" in str(result)


class TestText2SqlResultLimiting:
    """Тесты ограничения результатов Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_results_limited_to_1000_rows(self, converter, mock_db_manager):
        """Проверить, что результаты ограничены до 1000 строк."""
        # Arrange
        large_result = [{"id": i, "name": f"User {i}"} for i in range(1500)]
        mock_db_manager.execute_query.return_value = large_result

        # Act
        result_text = await converter.execute_and_format(
            "SELECT * FROM users",
            max_rows=1000
        )

        # Assert
        assert result_text is not None
        # Проверяем, что в результате не более 1000 строк
        lines = result_text.strip().split('\n')
        # Вычитаем заголовок и разделитель markdown таблицы
        data_lines = [l for l in lines if l.strip() and not l.startswith('|') or '|' in l]
        assert len(data_lines) <= 1002  # 1000 + header + separator

    @pytest.mark.asyncio
    async def test_results_formatting_as_table(self, converter, mock_db_manager):
        """Проверить форматирование результатов как markdown таблицы."""
        # Arrange
        mock_result = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        mock_db_manager.execute_query.return_value = mock_result

        # Act
        result = await converter.execute_and_format("SELECT * FROM users")

        # Assert
        assert "|" in result  # Markdown table format
        assert "id" in result
        assert "Alice" in result


class TestText2SqlErrorHandling:
    """Тесты обработки ошибок Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_llm_timeout_recovery(self, converter, mock_llm_client):
        """Проверить recovery при LLM timeout."""
        # Arrange
        question = "How many users are active?"
        mock_llm_client.generate.side_effect = asyncio.TimeoutError()

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await converter.convert(question)

    @pytest.mark.asyncio
    async def test_sql_error_handling(self, converter, mock_db_manager, mock_llm_client):
        """Проверить обработку SQL ошибок."""
        # Arrange
        question = "How many users are active?"
        mock_llm_client.generate.return_value = "SELECT * FROM nonexistent_table"
        mock_db_manager.execute_query.side_effect = Exception("Table not found")

        # Act
        with pytest.raises(Exception):
            response = await converter.convert(question)
            await converter.execute_and_format(response.sql)

    @pytest.mark.asyncio
    async def test_no_results_handling(self, converter, mock_db_manager, mock_llm_client):
        """Проверить обработку пустых результатов."""
        # Arrange
        mock_llm_client.generate.return_value = "SELECT * FROM users WHERE id > 1000000"
        mock_db_manager.execute_query.return_value = []

        # Act
        response = await converter.convert("How many old users?")
        result = await converter.execute_and_format(response.sql)

        # Assert
        assert "No results" in result or len(result) > 0  # Graceful handling


class TestText2SqlLogging:
    """Тесты логирования Text2SqlConverter."""

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
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def converter(self, mock_llm_client, mock_db_manager, mock_logger):
        """Создать Text2SqlConverter с mock зависимостями."""
        return Text2SqlConverter(mock_llm_client, mock_db_manager, mock_logger)

    @pytest.mark.asyncio
    async def test_logs_text2sql_operation(self, converter, mock_llm_client, mock_logger):
        """Проверить, что Text-to-SQL операция логируется."""
        # Arrange
        question = "How many users are active?"
        mock_llm_client.generate.return_value = "SELECT COUNT(*) FROM users"

        # Act
        await converter.convert(question)

        # Assert
        mock_logger.info.assert_called()
        # Проверяем, что в логе упоминается вопрос или SQL
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("convert" in str(call).lower() or "sql" in str(call).lower() for call in log_calls)
