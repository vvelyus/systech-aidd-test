"""Tests for LLMClient module."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm_client import LLMClient


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def llm_client(mock_logger):
    """Create a LLMClient instance with mocked dependencies."""
    with patch("src.llm_client.AsyncOpenAI"):
        client = LLMClient(
            api_key="test_key",
            model="test_model",
            base_url="https://test.api",
            system_prompt="Test system prompt",
            logger=mock_logger,
        )
        return client


@pytest.mark.asyncio
async def test_get_response_with_context_first_message(llm_client, mock_logger):
    """Test getting response with context for first message."""
    # Mock the API call
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    user_id = 12345
    user_message = "Hello, bot!"

    response = await llm_client.get_response_with_context(user_id, user_message)

    assert response == "Test response"
    assert user_id in llm_client.history
    assert len(llm_client.history[user_id]) == 2  # user message + assistant response
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_get_response_with_context_maintains_history(llm_client):
    """Test that context is maintained across multiple messages."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    user_id = 12345

    # Send multiple messages
    await llm_client.get_response_with_context(user_id, "Message 1")
    await llm_client.get_response_with_context(user_id, "Message 2")
    await llm_client.get_response_with_context(user_id, "Message 3")

    # Should have 6 messages: 3 user + 3 assistant
    assert len(llm_client.history[user_id]) == 6


@pytest.mark.asyncio
async def test_get_response_with_context_limits_history(llm_client):
    """Test that context history is limited to MAX_CONTEXT_MESSAGES."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    user_id = 12345

    # Send more messages than the limit (20 is the max)
    for i in range(25):
        await llm_client.get_response_with_context(user_id, f"Message {i}")

    # History should be limited to 20
    assert len(llm_client.history[user_id]) <= 20


def test_reset_context(llm_client, mock_logger):
    """Test resetting user context."""
    user_id = 12345

    # Add some context
    llm_client.history[user_id] = [{"role": "user", "content": "test"}]

    # Reset context
    llm_client.reset_context(user_id)

    assert user_id not in llm_client.history
    mock_logger.info.assert_called_with(f"Context reset for user_id={user_id}")


def test_reset_context_for_nonexistent_user(llm_client, mock_logger):
    """Test resetting context for user with no history."""
    user_id = 99999

    # Should not raise error
    llm_client.reset_context(user_id)

    assert user_id not in llm_client.history


def test_add_to_context(llm_client):
    """Test adding messages to context."""
    user_id = 12345

    llm_client._add_to_context(user_id, "user", "Test message")

    assert user_id in llm_client.history
    assert len(llm_client.history[user_id]) == 1
    assert llm_client.history[user_id][0]["role"] == "user"
    assert llm_client.history[user_id][0]["content"] == "Test message"


def test_get_context(llm_client):
    """Test getting context for user."""
    user_id = 12345

    # Add some context
    llm_client.history[user_id] = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]

    context = llm_client._get_context(user_id)

    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[1]["role"] == "assistant"


def test_get_context_for_new_user(llm_client):
    """Test getting context for user with no history."""
    user_id = 99999

    context = llm_client._get_context(user_id)

    assert context == []

