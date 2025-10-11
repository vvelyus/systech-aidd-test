"""Shared pytest fixtures for all tests."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User

from src.llm_client import LLMClient


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = MagicMock()
    client.get_response_with_context = AsyncMock(return_value="LLM response")
    client.reset_context = MagicMock()
    return client


@pytest.fixture
def llm_client(mock_logger):
    """Create a real LLMClient instance with mocked AsyncOpenAI."""
    with patch("src.llm_client.AsyncOpenAI"):
        return LLMClient(
            api_key="test_key",
            model="test_model",
            base_url="https://test.api",
            system_prompt="Test system prompt",
            logger=mock_logger,
        )


@pytest.fixture
def mock_message():
    """Create a mock Telegram Message object."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.text = "Test message"
    message.chat = MagicMock()
    message.chat.id = 12345
    message.answer = AsyncMock()
    return message

