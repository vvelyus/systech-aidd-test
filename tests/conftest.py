"""Shared pytest fixtures for all tests."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.context_storage import DatabaseContextStorage, InMemoryContextStorage
from src.database import DatabaseManager
from src.llm_client import LLMClient
from src.models import Base


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def context_storage(mock_logger):
    """Create a real InMemoryContextStorage instance."""
    return InMemoryContextStorage(max_messages=20, max_users=1000, logger=mock_logger)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = MagicMock()
    client.get_response_with_context = AsyncMock(return_value="LLM response")
    client.reset_context = AsyncMock()
    return client


@pytest.fixture
def llm_client(mock_logger, context_storage):
    """Create a real LLMClient instance with mocked AsyncOpenAI."""
    with patch("src.llm_client.AsyncOpenAI"):
        return LLMClient(
            api_key="test_key",
            model="test_model",
            base_url="https://test.api",
            system_prompt="Test system prompt",
            logger=mock_logger,
            context_storage=context_storage,
        )


@pytest.fixture
def mock_message():
    """Create a mock Telegram Message object."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.from_user.language_code = "en"
    message.text = "Test message"
    message.chat = MagicMock()
    message.chat.id = 12345
    message.answer = AsyncMock()
    return message


# Database fixtures for Sprint S1


@pytest.fixture
async def db_engine():
    """Create an in-memory async SQLite engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create an async database session for testing."""
    async_session_factory = sessionmaker(  # type: ignore[call-overload]
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes


@pytest.fixture
async def database_context_storage(db_session, mock_logger):
    """Create a DatabaseContextStorage instance for testing."""
    storage = DatabaseContextStorage(
        session=db_session, max_messages=20, logger=mock_logger
    )
    yield storage
    await storage.close()


@pytest.fixture
def database_manager(mock_logger):
    """Create a DatabaseManager instance for testing."""
    manager = DatabaseManager(
        database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
    )
    return manager
