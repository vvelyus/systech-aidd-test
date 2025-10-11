"""Тесты для модуля context_storage."""

import pytest

from src.context_storage import InMemoryContextStorage


def test_add_message_creates_new_user(context_storage):
    """Test adding message for a new user."""
    context_storage.add_message(123, "user", "Hello")
    context = context_storage.get_context(123)
    assert len(context) == 1
    assert context[0] == {"role": "user", "content": "Hello"}


def test_add_message_appends_to_existing_context(context_storage):
    """Test adding multiple messages to existing context."""
    context_storage.add_message(123, "user", "Hello")
    context_storage.add_message(123, "assistant", "Hi")
    context_storage.add_message(123, "user", "How are you?")

    context = context_storage.get_context(123)
    assert len(context) == 3
    assert context[0]["content"] == "Hello"
    assert context[1]["content"] == "Hi"
    assert context[2]["content"] == "How are you?"


def test_add_message_trims_context_to_max_messages(mock_logger):
    """Test that context is trimmed to max_messages."""
    storage = InMemoryContextStorage(max_messages=3, logger=mock_logger)

    # Add 5 messages
    for i in range(5):
        storage.add_message(123, "user", f"Message {i}")

    context = storage.get_context(123)
    # Should keep only last 3
    assert len(context) == 3
    assert context[0]["content"] == "Message 2"
    assert context[1]["content"] == "Message 3"
    assert context[2]["content"] == "Message 4"


def test_get_context_empty_for_new_user(context_storage):
    """Test getting context for user with no messages."""
    context = context_storage.get_context(999)
    assert context == []


def test_reset_context_removes_user_messages(context_storage):
    """Test resetting context removes all messages."""
    context_storage.add_message(123, "user", "Hello")
    context_storage.add_message(123, "assistant", "Hi")

    context_storage.reset_context(123)

    context = context_storage.get_context(123)
    assert context == []


def test_reset_context_for_nonexistent_user(context_storage):
    """Test resetting context for user with no messages."""
    # Should not raise error
    context_storage.reset_context(999)
    context = context_storage.get_context(999)
    assert context == []


def test_get_user_count(context_storage):
    """Test getting number of users in storage."""
    assert context_storage.get_user_count() == 0

    context_storage.add_message(123, "user", "Hello")
    assert context_storage.get_user_count() == 1

    context_storage.add_message(456, "user", "Hi")
    assert context_storage.get_user_count() == 2

    context_storage.reset_context(123)
    assert context_storage.get_user_count() == 1


def test_clear_all(context_storage):
    """Test clearing all data from storage."""
    context_storage.add_message(123, "user", "Hello")
    context_storage.add_message(456, "user", "Hi")

    assert context_storage.get_user_count() == 2

    context_storage.clear_all()

    assert context_storage.get_user_count() == 0
    assert context_storage.get_context(123) == []
    assert context_storage.get_context(456) == []


def test_max_users_limit(mock_logger):
    """Test that storage enforces max_users limit."""
    storage = InMemoryContextStorage(max_messages=20, max_users=3, logger=mock_logger)

    # Add messages for 4 users (exceeds limit)
    for user_id in [100, 200, 300, 400]:
        storage.add_message(user_id, "user", f"Message from {user_id}")

    # Should have only 3 users (oldest removed)
    assert storage.get_user_count() == 3

    # First user should be removed
    assert storage.get_context(100) == []

    # Other users should exist
    assert len(storage.get_context(200)) == 1
    assert len(storage.get_context(300)) == 1
    assert len(storage.get_context(400)) == 1


def test_context_storage_protocol_compliance():
    """Test that InMemoryContextStorage implements ContextStorage protocol."""
    from src.context_storage import ContextStorage

    storage = InMemoryContextStorage()

    # Check that all protocol methods exist
    assert hasattr(storage, "add_message")
    assert hasattr(storage, "get_context")
    assert hasattr(storage, "reset_context")

    # Check that methods are callable
    assert callable(storage.add_message)
    assert callable(storage.get_context)
    assert callable(storage.reset_context)


def test_multiple_users_isolated_contexts(context_storage):
    """Test that contexts for different users are isolated."""
    context_storage.add_message(123, "user", "User 123 message")
    context_storage.add_message(456, "user", "User 456 message")

    context_123 = context_storage.get_context(123)
    context_456 = context_storage.get_context(456)

    assert len(context_123) == 1
    assert len(context_456) == 1
    assert context_123[0]["content"] == "User 123 message"
    assert context_456[0]["content"] == "User 456 message"

