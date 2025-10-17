"""Tests for database manager (Sprint S1, S2)."""

import logging

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import DatabaseManager


@pytest.mark.asyncio
class TestDatabaseManager:
    """Tests for DatabaseManager class."""

    async def test_init(self, mock_logger):
        """Test DatabaseManager initialization."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        assert manager._engine is not None
        assert manager._async_session_factory is not None
        assert manager._logger is mock_logger

        # Cleanup
        await manager.close()

    async def test_init_db(self, mock_logger):
        """Test database schema initialization."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        # Should not raise an exception
        await manager.init_db()

        # Verify logger was called
        mock_logger.info.assert_any_call("Database schema initialized (if not already present)")

        # Cleanup
        await manager.close()

    async def test_get_session(self, mock_logger):
        """Test getting a database session."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Get a session using async context manager
        async with manager.get_session() as session:
            assert isinstance(session, AsyncSession)
            # Session should be usable
            assert session is not None

        # Cleanup
        await manager.close()

    async def test_session_commit_on_success(self, mock_logger):
        """Test that session commits on successful operation."""
        from sqlalchemy import select

        from src.models import Message

        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create a message using the session
        async with manager.get_session() as session:
            message = Message(
                user_id=12345, role="user", content="Test", length=4
            )
            session.add(message)
            # Session should commit automatically on exit

        # Verify the message was committed
        async with manager.get_session() as session:
            stmt = select(Message).where(Message.user_id == 12345)
            result = await session.execute(stmt)
            retrieved = result.scalar_one_or_none()

            assert retrieved is not None
            assert retrieved.content == "Test"

        # Cleanup
        await manager.close()

    async def test_session_rollback_on_error(self, mock_logger):
        """Test that session rolls back on error."""
        from sqlalchemy import select

        from src.models import Message

        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Try to create a message and raise an error
        with pytest.raises(RuntimeError, match="Test error"):
            async with manager.get_session() as session:
                message = Message(
                    user_id=12345, role="user", content="Test", length=4
                )
                session.add(message)
                await session.flush()
                # Raise an error before commit
                raise RuntimeError("Test error")

        # Verify the message was NOT committed
        async with manager.get_session() as session:
            stmt = select(Message).where(Message.user_id == 12345)
            result = await session.execute(stmt)
            retrieved = result.scalar_one_or_none()

            assert retrieved is None  # Should be rolled back

        # Cleanup
        await manager.close()

    async def test_close(self, mock_logger):
        """Test closing database connection."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()
        await manager.close()

        # Verify logger was called
        mock_logger.info.assert_any_call("Database connection pool disposed")

    async def test_multiple_sessions(self, mock_logger):
        """Test creating multiple sessions from the same manager."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create multiple sessions
        async with manager.get_session() as session1:
            assert isinstance(session1, AsyncSession)

        async with manager.get_session() as session2:
            assert isinstance(session2, AsyncSession)

        # Sessions should be different instances
        assert session1 is not session2

        # Cleanup
        await manager.close()

    async def test_database_url_logging(self, mock_logger):
        """Test that database URL is logged on initialization."""
        database_url = "sqlite+aiosqlite:///:memory:"

        DatabaseManager(database_url=database_url, logger=mock_logger)

        # Verify logger was called with the database URL
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any(database_url in str(call) for call in calls)

    async def test_upsert_user_create(self, mock_logger):
        """Test creating a new user with upsert_user (Sprint S2)."""
        from sqlalchemy import select

        from src.models import User

        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create a new user
        user = await manager.upsert_user(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="en",
        )

        assert user.telegram_id == 12345
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.language_code == "en"

        # Verify user was saved
        async with manager.get_session() as session:
            stmt = select(User).where(User.telegram_id == 12345)
            result = await session.execute(stmt)
            retrieved = result.scalar_one()

            assert retrieved.username == "testuser"

        # Cleanup
        await manager.close()

    async def test_upsert_user_update(self, mock_logger):
        """Test updating existing user with upsert_user (Sprint S2)."""
        from sqlalchemy import select

        from src.models import User

        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create a user
        await manager.upsert_user(
            telegram_id=12345,
            username="oldname",
            first_name="Old",
            last_name="Name",
            language_code="en",
        )

        # Update the same user
        updated_user = await manager.upsert_user(
            telegram_id=12345,
            username="newname",
            first_name="New",
            last_name="Name",
            language_code="ru",
        )

        assert updated_user.telegram_id == 12345
        assert updated_user.username == "newname"
        assert updated_user.first_name == "New"
        assert updated_user.last_name == "Name"
        assert updated_user.language_code == "ru"

        # Verify only one user exists
        async with manager.get_session() as session:
            stmt = select(User).where(User.telegram_id == 12345)
            result = await session.execute(stmt)
            all_users = result.scalars().all()

            assert len(all_users) == 1
            assert all_users[0].username == "newname"

        # Cleanup
        await manager.close()

    async def test_upsert_user_with_none_values(self, mock_logger):
        """Test upsert_user with None values (Sprint S2)."""
        from sqlalchemy import select

        from src.models import User

        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create user with None values
        user = await manager.upsert_user(
            telegram_id=12345,
            username=None,
            first_name=None,
            last_name=None,
            language_code=None,
        )

        assert user.telegram_id == 12345
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.language_code is None

        # Cleanup
        await manager.close()

    async def test_upsert_user_logging(self, mock_logger):
        """Test that upsert_user logs correctly (Sprint S2)."""
        manager = DatabaseManager(
            database_url="sqlite+aiosqlite:///:memory:", logger=mock_logger
        )

        await manager.init_db()

        # Create new user - should log "Created new user"
        await manager.upsert_user(telegram_id=12345, username="test")

        # Check logger was called with create message
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Created new user" in str(call) and "12345" in str(call) for call in calls)

        # Update user - should log "Updated user"
        mock_logger.reset_mock()
        await manager.upsert_user(telegram_id=12345, username="updated")

        # Check logger was called with update message
        calls = [str(call) for call in mock_logger.debug.call_args_list]
        assert any("Updated user" in str(call) and "12345" in str(call) for call in calls)

        # Cleanup
        await manager.close()
