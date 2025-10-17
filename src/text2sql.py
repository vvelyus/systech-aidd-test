"""Text-to-SQL конвертор для преобразования вопросов в SQL запросы."""

import asyncio
import hashlib
import logging
import time
from typing import TYPE_CHECKING, Optional, Tuple

import sqlparse
from src.api.models import TextToSqlResponse

if TYPE_CHECKING:
    from src.llm_client import LLMClient
    from src.database import DatabaseManager


class Text2SqlConverter:
    """Конвертор для преобразования вопросов на естественном языке в SQL запросы."""

    # Схема БД для use case из messages таблицы
    DB_SCHEMA = """
    -- Таблица пользователей
    CREATE TABLE users (
        telegram_id INT PRIMARY KEY,
        username VARCHAR(32),
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        language_code VARCHAR(10),
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );

    -- Таблица сообщений диалогов
    CREATE TABLE messages (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        role VARCHAR(20) NOT NULL,  -- 'user' или 'assistant'
        content TEXT NOT NULL,
        length INT NOT NULL,
        created_at TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(telegram_id)
    );
    """

    def __init__(
        self,
        llm_client: "LLMClient",
        db_manager: "DatabaseManager",
        logger: logging.Logger,
        cache_ttl: int = 3600,
    ) -> None:
        """
        Инициализация конвертора.

        Args:
            llm_client: Клиент для LLM
            db_manager: Менеджер базы данных
            logger: Логгер
            cache_ttl: Time-to-live для кеша в секундах (по умолчанию 1 час)
        """
        self.llm_client = llm_client
        self.db_manager = db_manager
        self.logger = logger
        self.cache: dict[str, Tuple[str, float]] = {}  # {question_hash: (sql, timestamp)}
        self.cache_ttl = cache_ttl
        self.schema_cache: Optional[str] = None
        self.schema_cache_time: float = 0

        # Security: whitelist operations
        self.allowed_keywords = {
            "SELECT", "WHERE", "JOIN", "GROUP", "ORDER", "LIMIT",
            "HAVING", "DISTINCT", "COUNT", "SUM", "AVG", "MAX", "MIN",
            "FROM", "LEFT", "RIGHT", "INNER", "OUTER", "ON", "AND", "OR",
            "BY", "AS", "WITH", "CASE", "WHEN", "THEN", "ELSE", "END"
        }
        self.forbidden_keywords = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"}

        self.logger.info("Text2SqlConverter initialized with caching and security features")

    def _hash_question(self, question: str) -> str:
        """Хешировать вопрос для использования в кеше."""
        return hashlib.md5(question.lower().encode()).hexdigest()

    def _check_cache(self, question: str) -> Optional[str]:
        """Проверить кеш и вернуть SQL если найден и не истек."""
        question_hash = self._hash_question(question)
        if question_hash in self.cache:
            sql, timestamp = self.cache[question_hash]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.info(f"Cache hit for question: {question[:50]}...")
                return sql
            else:
                # Кеш истек
                del self.cache[question_hash]
                self.logger.info(f"Cache expired for question: {question[:50]}...")
        return None

    def _cache_sql(self, question: str, sql: str) -> None:
        """Кешировать SQL запрос."""
        question_hash = self._hash_question(question)
        self.cache[question_hash] = (sql, time.time())
        self.logger.info(f"Cached SQL for question: {question[:50]}...")

    def _validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Валидировать SQL запрос.

        Returns:
            (is_valid, error_message)
        """
        try:
            # Parse SQL
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Invalid SQL: cannot parse"

            # Get keywords from SQL
            sql_upper = sql.upper()

            # Check forbidden keywords
            for forbidden in self.forbidden_keywords:
                if forbidden in sql_upper:
                    return False, f"Forbidden operation: {forbidden}"

            # Check if SELECT is present
            if "SELECT" not in sql_upper:
                return False, "Only SELECT queries are allowed"

            # Basic structure validation
            if sql_upper.count("SELECT") > 1:
                return False, "Multiple SELECT not allowed"

            return True, None
        except Exception as e:
            return False, f"SQL validation error: {str(e)}"

    async def convert(
        self,
        question: str,
        context: Optional[dict] = None,
        max_retries: int = 3
    ) -> TextToSqlResponse:
        """
        Преобразовать вопрос в SQL запрос.

        Args:
            question: Вопрос на естественном языке
            context: Дополнительный контекст
            max_retries: Максимальное количество попыток

        Returns:
            TextToSqlResponse с SQL запросом и объяснением
        """
        # Check cache first
        cached_sql = self._check_cache(question)
        if cached_sql:
            return TextToSqlResponse(
                sql=cached_sql,
                explanation="Retrieved from cache",
                is_cached=True
            )

        # Try to generate SQL with retries
        for attempt in range(max_retries):
            try:
                system_prompt = f"""You are a SQL expert. Convert the natural language question to a SQL query.
Use this database schema:
{self.DB_SCHEMA}

Return ONLY the SQL query, nothing else. Do not include markdown formatting."""

                response = await asyncio.wait_for(
                    self.llm_client.get_response(
                        f"{system_prompt}\n\nQuestion: {question}"
                    ),
                    timeout=5.0  # 5 second timeout per LLM call
                )

                # Extract SQL from response (remove markdown if present)
                sql = response.strip()
                if sql.startswith("```"):
                    sql = sql.split("\n", 1)[1] if "\n" in sql else sql
                if sql.endswith("```"):
                    sql = sql[:-3]
                sql = sql.strip()

                # Validate SQL
                is_valid, error = self._validate_sql(sql)
                if not is_valid:
                    self.logger.warning(f"SQL validation failed: {error}")
                    if attempt < max_retries - 1:
                        continue
                    return TextToSqlResponse(
                        sql="",
                        explanation=f"Could not generate valid SQL: {error}",
                        is_cached=False,
                        error=error
                    )

                # Cache the successful SQL
                self._cache_sql(question, sql)

                return TextToSqlResponse(
                    sql=sql,
                    explanation=f"Generated SQL query (attempt {attempt + 1})",
                    is_cached=False
                )

            except asyncio.TimeoutError:
                self.logger.warning(f"LLM timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
            except Exception as e:
                self.logger.error(f"Error generating SQL on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue

        return TextToSqlResponse(
            sql="",
            explanation="Failed to generate SQL after multiple attempts",
            is_cached=False,
            error="LLM timeout or error after retries"
        )

    async def execute_and_format(
        self,
        sql: str,
        max_rows: int = 1000,
        timeout: float = 5.0
    ) -> str:
        """
        Выполняет SQL запрос и форматирует результаты.

        Args:
            sql: SQL запрос для выполнения
            max_rows: Максимальное количество строк для возврата (по умолчанию 1000)
            timeout: Таймаут для выполнения запроса в секундах (по умолчанию 5.0)

        Returns:
            Отформатированные результаты как строка
        """
        try:
            session = self.db_manager.create_session()
            from sqlalchemy import text

            result = await asyncio.wait_for(
                session.execute(text(sql)),
                timeout=timeout
            )
            rows = result.fetchall()

            if not rows:
                return "Результаты не найдены"

            # Ограничиваем количество строк, если max_rows установлен
            if max_rows > 0 and len(rows) > max_rows:
                rows = rows[:max_rows]

            # Форматируем результаты в таблицу
            formatted = self._format_table(rows)
            self.logger.info(f"SQL query executed successfully, {len(rows)} rows returned")

            return formatted

        except asyncio.TimeoutError:
            self.logger.error(f"SQL query execution timed out after {timeout} seconds")
            return f"Запрос выполнен не полностью из-за таймаута ({timeout} сек)"
        except Exception as e:
            self.logger.error(f"Error executing SQL query: {e}")
            return f"Ошибка при выполнении запроса: {str(e)}"

    def _extract_sql(self, response: str) -> str:
        """Извлекает SQL запрос из ответа LLM."""
        # Ищем SQL в markdown блоке
        if "```sql" in response:
            start = response.find("```sql") + 7
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        # Fallback: ищем SELECT
        if "SELECT" in response:
            lines = response.split("\n")
            for line in lines:
                if "SELECT" in line.upper():
                    return line.strip()

        return response.strip()

    def _extract_explanation(self, response: str) -> str:
        """Извлекает объяснение из ответа LLM."""
        if "Объяснение:" in response:
            start = response.find("Объяснение:") + 11
            return response[start:].strip()
        return "SQL запрос для анализа данных"

    def _format_table(self, rows: list) -> str:
        """Форматирует результаты в таблицу."""
        if not rows:
            return "Нет результатов"

        # Получаем заголовки (если это Row объекты)
        headers = []
        if hasattr(rows[0], "keys"):
            headers = list(rows[0].keys())
        elif hasattr(rows[0], "_fields"):
            headers = list(rows[0]._fields)
        else:
            headers = [f"Column {i}" for i in range(len(rows[0]))]

        # Форматируем таблицу
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in rows:
            if hasattr(row, "values"):
                values = list(row.values())
            else:
                values = list(row)
            lines.append("| " + " | ".join(str(v) for v in values) + " |")

        return "\n".join(lines)
