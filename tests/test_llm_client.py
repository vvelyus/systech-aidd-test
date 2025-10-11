"""Tests for LLMClient module."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_get_response_with_context_first_message(llm_client, context_storage, mock_logger):
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
    context = context_storage.get_context(user_id)
    assert len(context) == 2  # user message + assistant response
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_get_response_with_context_maintains_history(llm_client, context_storage):
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
    context = context_storage.get_context(user_id)
    assert len(context) == 6


@pytest.mark.asyncio
async def test_get_response_with_context_limits_history(llm_client, context_storage):
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
    context = context_storage.get_context(user_id)
    assert len(context) <= 20


def test_reset_context(llm_client, context_storage, mock_logger):
    """Test resetting user context."""
    user_id = 12345

    # Add some context
    context_storage.add_message(user_id, "user", "test")

    # Reset context
    llm_client.reset_context(user_id)

    context = context_storage.get_context(user_id)
    assert context == []
    mock_logger.info.assert_called_with(f"Context reset for user_id={user_id}")


def test_reset_context_for_nonexistent_user(llm_client, context_storage, mock_logger):
    """Test resetting context for user with no history."""
    user_id = 99999

    # Should not raise error
    llm_client.reset_context(user_id)

    context = context_storage.get_context(user_id)
    assert context == []


@pytest.mark.asyncio
async def test_get_response_without_context(llm_client, mock_logger):
    """Test getting response without context (single message)."""
    # Mock the API call
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Simple response"

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    user_message = "Hello, world!"

    response = await llm_client.get_response(user_message)

    assert response == "Simple response"
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_get_response_empty_response_from_llm(llm_client):
    """Test handling empty response from LLM."""
    # Mock the API call with empty content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = None  # Empty!

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Should raise ValueError for empty response
    with pytest.raises(ValueError, match="Empty response"):
        await llm_client.get_response("Hello")


@pytest.mark.asyncio
async def test_get_response_api_error(llm_client, mock_logger):
    """Test error handling when API fails."""
    # Mock API to raise exception
    llm_client.client.chat.completions.create = AsyncMock(
        side_effect=Exception("API connection error")
    )

    # Should propagate the exception
    with pytest.raises(Exception, match="API connection error"):
        await llm_client.get_response("Hello")

    # Should log the error
    mock_logger.error.assert_called()


@pytest.mark.asyncio
async def test_get_response_with_context_empty_response(llm_client):
    """Test handling empty response from LLM with context."""
    # Mock the API call with empty content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = None  # Empty!

    llm_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    user_id = 12345

    # Should raise ValueError for empty response
    with pytest.raises(ValueError, match="Empty response"):
        await llm_client.get_response_with_context(user_id, "Hello")


@pytest.mark.asyncio
async def test_get_response_with_context_api_error(llm_client, mock_logger):
    """Test error handling when API fails with context."""
    # Mock API to raise exception
    llm_client.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

    user_id = 12345

    # Should propagate the exception
    with pytest.raises(Exception, match="API Error"):
        await llm_client.get_response_with_context(user_id, "Hello")

    # Should log the error
    mock_logger.error.assert_called()

