"""Тесты для модуля context_storage."""

import pytest

from src.context_storage import DatabaseContextStorage, InMemoryContextStorage


# Tests for InMemoryContextStorage


@pytest.mark.asyncio
async def test_add_message_creates_new_user(context_storage):
    """Test adding message for a new user."""
    await context_storage.add_message(123, "user", "Hello")
    context = await context_storage.get_context(123)
    assert len(context) == 1
    assert context[0] == {"role": "user", "content": "Hello"}


@pytest.mark.asyncio
async def test_add_message_appends_to_existing_context(context_storage):
    """Test adding multiple messages to existing context."""
    await context_storage.add_message(123, "user", "Hello")
    await context_storage.add_message(123, "assistant", "Hi")
    await context_storage.add_message(123, "user", "How are you?")

    context = await context_storage.get_context(123)
    assert len(context) == 3
    assert context[0]["content"] == "Hello"
    assert context[1]["content"] == "Hi"
    assert context[2]["content"] == "How are you?"


@pytest.mark.asyncio
async def test_add_message_trims_context_to_max_messages(mock_logger):
    """Test that context is trimmed to max_messages."""
    storage = InMemoryContextStorage(max_messages=3, logger=mock_logger)

    # Add 5 messages
    for i in range(5):
        await storage.add_message(123, "user", f"Message {i}")

    context = await storage.get_context(123)
    # Should keep only last 3
    assert len(context) == 3
    assert context[0]["content"] == "Message 2"
    assert context[1]["content"] == "Message 3"
    assert context[2]["content"] == "Message 4"


@pytest.mark.asyncio
async def test_get_context_empty_for_new_user(context_storage):
    """Test getting context for user with no messages."""
    context = await context_storage.get_context(999)
    assert context == []


@pytest.mark.asyncio
async def test_reset_context_removes_user_messages(context_storage):
    """Test resetting context removes all messages."""
    await context_storage.add_message(123, "user", "Hello")
    await context_storage.add_message(123, "assistant", "Hi")

    await context_storage.reset_context(123)

    context = await context_storage.get_context(123)
    assert context == []


@pytest.mark.asyncio
async def test_reset_context_for_nonexistent_user(context_storage):
    """Test resetting context for user with no messages."""
    # Should not raise error
    await context_storage.reset_context(999)
    context = await context_storage.get_context(999)
    assert context == []


def test_get_user_count(context_storage):
    """Test getting number of users in storage."""
    assert context_storage.get_user_count() == 0

    # Note: InMemoryContextStorage has sync methods for stats


@pytest.mark.asyncio
async def test_get_user_count_async(context_storage):
    """Test getting number of users in storage (async version)."""
    assert context_storage.get_user_count() == 0

    await context_storage.add_message(123, "user", "Hello")
    assert context_storage.get_user_count() == 1

    await context_storage.add_message(456, "user", "Hi")
    assert context_storage.get_user_count() == 2

    await context_storage.reset_context(123)
    assert context_storage.get_user_count() == 1


@pytest.mark.asyncio
async def test_clear_all(context_storage):
    """Test clearing all data from storage."""
    await context_storage.add_message(123, "user", "Hello")
    await context_storage.add_message(456, "user", "Hi")

    assert context_storage.get_user_count() == 2

    context_storage.clear_all()

    assert context_storage.get_user_count() == 0
    assert await context_storage.get_context(123) == []
    assert await context_storage.get_context(456) == []


@pytest.mark.asyncio
async def test_max_users_limit(mock_logger):
    """Test that storage enforces max_users limit."""
    storage = InMemoryContextStorage(max_messages=20, max_users=3, logger=mock_logger)

    # Add messages for 4 users (exceeds limit)
    for user_id in [100, 200, 300, 400]:
        await storage.add_message(user_id, "user", f"Message from {user_id}")

    # Should have only 3 users (oldest removed)
    assert storage.get_user_count() == 3

    # First user should be removed
    assert await storage.get_context(100) == []

    # Other users should exist
    assert len(await storage.get_context(200)) == 1
    assert len(await storage.get_context(300)) == 1
    assert len(await storage.get_context(400)) == 1


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


@pytest.mark.asyncio
async def test_multiple_users_isolated_contexts(context_storage):
    """Test that contexts for different users are isolated."""
    await context_storage.add_message(123, "user", "User 123 message")
    await context_storage.add_message(456, "user", "User 456 message")

    context_123 = await context_storage.get_context(123)
    context_456 = await context_storage.get_context(456)

    assert len(context_123) == 1
    assert len(context_456) == 1
    assert context_123[0]["content"] == "User 123 message"
    assert context_456[0]["content"] == "User 456 message"


# Tests for DatabaseContextStorage (Sprint S1)


@pytest.mark.asyncio
class TestDatabaseContextStorage:
    """Tests for DatabaseContextStorage class."""

    async def test_add_message_saves_to_database(self, database_context_storage, db_session):
        """Test that add_message saves to database."""
        from sqlalchemy import select

        from src.models import Message

        await database_context_storage.add_message(12345, "user", "Hello database")

        # Query database directly
        stmt = select(Message).where(Message.user_id == 12345)
        result = await db_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello database"
        assert messages[0].length == len("Hello database")
        assert messages[0].is_deleted is False

    async def test_add_message_calculates_length(self, database_context_storage, db_session):
        """Test that length is calculated correctly."""
        from sqlalchemy import select

        from src.models import Message

        content = "This is a test message"
        await database_context_storage.add_message(12345, "user", content)

        stmt = select(Message).where(Message.user_id == 12345)
        result = await db_session.execute(stmt)
        message = result.scalar_one()

        assert message.length == len(content)

    async def test_get_context_retrieves_messages(self, database_context_storage):
        """Test that get_context retrieves messages from database."""
        await database_context_storage.add_message(12345, "user", "First")
        await database_context_storage.add_message(12345, "assistant", "Second")
        await database_context_storage.add_message(12345, "user", "Third")

        context = await database_context_storage.get_context(12345)

        assert len(context) == 3
        assert context[0] == {"role": "user", "content": "First"}
        assert context[1] == {"role": "assistant", "content": "Second"}
        assert context[2] == {"role": "user", "content": "Third"}

    async def test_get_context_limits_to_max_messages(self, db_session, mock_logger):
        """Test that get_context respects max_messages limit."""
        storage = DatabaseContextStorage(session=db_session, max_messages=3, logger=mock_logger)

        # Add 5 messages
        for i in range(5):
            await storage.add_message(12345, "user", f"Message {i}")

        context = await storage.get_context(12345)

        # Should return only last 3 messages
        assert len(context) == 3
        assert context[0]["content"] == "Message 2"
        assert context[1]["content"] == "Message 3"
        assert context[2]["content"] == "Message 4"

    async def test_get_context_empty_for_new_user(self, database_context_storage):
        """Test that get_context returns empty list for new user."""
        context = await database_context_storage.get_context(99999)
        assert context == []

    async def test_reset_context_soft_delete(self, database_context_storage, db_session):
        """Test that reset_context performs soft delete."""
        from sqlalchemy import select

        from src.models import Message

        # Add messages
        await database_context_storage.add_message(12345, "user", "Message 1")
        await database_context_storage.add_message(12345, "user", "Message 2")

        # Reset context
        await database_context_storage.reset_context(12345)

        # Messages should still exist in database but marked as deleted
        stmt = select(Message).where(Message.user_id == 12345)
        result = await db_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) == 2
        assert all(msg.is_deleted is True for msg in messages)

        # get_context should return empty
        context = await database_context_storage.get_context(12345)
        assert context == []

    async def test_reset_context_only_affects_target_user(self, database_context_storage, db_session):
        """Test that reset_context only deletes messages for the target user."""
        from sqlalchemy import select

        from src.models import Message

        # Add messages for two users
        await database_context_storage.add_message(12345, "user", "User 1 message")
        await database_context_storage.add_message(67890, "user", "User 2 message")

        # Reset context for user 1
        await database_context_storage.reset_context(12345)

        # User 1 messages should be deleted
        context_1 = await database_context_storage.get_context(12345)
        assert context_1 == []

        # User 2 messages should remain
        context_2 = await database_context_storage.get_context(67890)
        assert len(context_2) == 1
        assert context_2[0]["content"] == "User 2 message"

    async def test_get_context_excludes_deleted_messages(self, database_context_storage, db_session):
        """Test that get_context excludes soft-deleted messages."""
        from sqlalchemy import update

        from src.models import Message

        # Add messages
        await database_context_storage.add_message(12345, "user", "Message 1")
        await database_context_storage.add_message(12345, "user", "Message 2")
        await database_context_storage.add_message(12345, "user", "Message 3")

        # Manually soft-delete one message
        stmt = (
            update(Message)
            .where(Message.user_id == 12345)
            .where(Message.content == "Message 2")
            .values(is_deleted=True)
        )
        await db_session.execute(stmt)
        await db_session.commit()

        # get_context should exclude deleted message
        context = await database_context_storage.get_context(12345)
        assert len(context) == 2
        assert context[0]["content"] == "Message 1"
        assert context[1]["content"] == "Message 3"

    async def test_close_closes_session(self, database_context_storage):
        """Test that close() closes the database session."""
        # Should not raise any exceptions
        await database_context_storage.close()

    async def test_context_storage_protocol_compliance_database(self, database_context_storage):
        """Test that DatabaseContextStorage implements ContextStorage protocol."""
        from src.context_storage import ContextStorage

        # Check that all protocol methods exist
        assert hasattr(database_context_storage, "add_message")
        assert hasattr(database_context_storage, "get_context")
        assert hasattr(database_context_storage, "reset_context")

        # Check that methods are callable
        assert callable(database_context_storage.add_message)
        assert callable(database_context_storage.get_context)
        assert callable(database_context_storage.reset_context)
