"""Tests for SQLAlchemy models (Sprint S1, S2)."""

import datetime

import pytest

from src.models import Message, User


class TestMessage:
    """Tests for the Message model."""

    def test_message_creation(self):
        """Test creating a Message instance with required fields."""
        message = Message(
            user_id=12345,
            role="user",
            content="Test message",
            length=12,
        )

        assert message.user_id == 12345
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.length == 12
        assert message.is_deleted is False

    def test_message_with_all_fields(self):
        """Test creating a Message with all fields including optional ones."""
        created_at = datetime.datetime.now()

        message = Message(
            id=1,
            user_id=12345,
            role="assistant",
            content="Response message",
            length=16,
            created_at=created_at,
            is_deleted=True,
        )

        assert message.id == 1
        assert message.user_id == 12345
        assert message.role == "assistant"
        assert message.content == "Response message"
        assert message.length == 16
        assert message.created_at == created_at
        assert message.is_deleted is True

    def test_message_repr(self):
        """Test the __repr__ method of Message."""
        message = Message(
            id=1,
            user_id=12345,
            role="user",
            content="Test",
            length=4,
            created_at=datetime.datetime(2025, 10, 16, 12, 0, 0),
            is_deleted=False,
        )

        repr_str = repr(message)

        assert "Message(" in repr_str
        assert "id=1" in repr_str
        assert "user_id=12345" in repr_str
        assert "role='user'" in repr_str
        assert "length=4" in repr_str
        assert "is_deleted=False" in repr_str

    def test_message_defaults(self):
        """Test that default values are set correctly."""
        message = Message(
            user_id=12345,
            role="user",
            content="Test",
            length=4,
        )

        # is_deleted should default to False
        assert message.is_deleted is False

    def test_message_role_user(self):
        """Test creating a message with role 'user'."""
        message = Message(
            user_id=12345,
            role="user",
            content="User message",
            length=12,
        )

        assert message.role == "user"

    def test_message_role_assistant(self):
        """Test creating a message with role 'assistant'."""
        message = Message(
            user_id=12345,
            role="assistant",
            content="Assistant message",
            length=17,
        )

        assert message.role == "assistant"


@pytest.mark.asyncio
class TestMessagePersistence:
    """Tests for Message model persistence in database."""

    async def test_save_and_retrieve_message(self, db_session):
        """Test saving a message to the database and retrieving it."""
        from sqlalchemy import select

        # Create and save a message
        message = Message(
            user_id=12345,
            role="user",
            content="Persistent message",
            length=18,
        )

        db_session.add(message)
        await db_session.flush()

        # Verify message has an ID assigned
        assert message.id is not None

        # Retrieve the message
        stmt = select(Message).where(Message.id == message.id)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.user_id == 12345
        assert retrieved.role == "user"
        assert retrieved.content == "Persistent message"
        assert retrieved.length == 18
        assert retrieved.is_deleted is False

    async def test_message_created_at_auto(self, db_session):
        """Test that created_at is set automatically."""
        from sqlalchemy import select

        # Create a message without setting created_at
        message = Message(
            user_id=12345,
            role="user",
            content="Test",
            length=4,
        )

        db_session.add(message)
        await db_session.commit()

        # Retrieve and check created_at
        stmt = select(Message).where(Message.id == message.id)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.created_at is not None
        assert isinstance(retrieved.created_at, datetime.datetime)

    async def test_soft_delete_flag(self, db_session):
        """Test that is_deleted flag works correctly."""
        from sqlalchemy import select

        # Create message with is_deleted=True
        message = Message(
            user_id=12345,
            role="user",
            content="Deleted message",
            length=15,
            is_deleted=True,
        )

        db_session.add(message)
        await db_session.commit()

        # Retrieve and verify
        stmt = select(Message).where(Message.id == message.id)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.is_deleted is True


class TestUser:
    """Tests for the User model (Sprint S2)."""

    def test_user_creation(self):
        """Test creating a User instance with required fields."""
        user = User(telegram_id=12345)

        assert user.telegram_id == 12345
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.language_code is None

    def test_user_with_all_fields(self):
        """Test creating a User with all fields."""
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        user = User(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="en",
            created_at=created_at,
            updated_at=updated_at,
        )

        assert user.telegram_id == 12345
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.language_code == "en"
        assert user.created_at == created_at
        assert user.updated_at == updated_at

    def test_user_repr(self):
        """Test the __repr__ method of User."""
        user = User(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            created_at=datetime.datetime(2025, 10, 16, 12, 0, 0),
        )

        repr_str = repr(user)

        assert "User(" in repr_str
        assert "telegram_id=12345" in repr_str
        assert "username='testuser'" in repr_str
        assert "first_name='Test'" in repr_str
        assert "last_name='User'" in repr_str

    def test_user_to_dict(self):
        """Test converting User to dictionary."""
        user = User(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="ru",
        )

        user_dict = user.to_dict()

        assert user_dict["telegram_id"] == 12345
        assert user_dict["username"] == "testuser"
        assert user_dict["first_name"] == "Test"
        assert user_dict["last_name"] == "User"
        assert user_dict["language_code"] == "ru"
        assert "created_at" in user_dict
        assert "updated_at" in user_dict


@pytest.mark.asyncio
class TestUserPersistence:
    """Tests for User model persistence in database (Sprint S2)."""

    async def test_save_and_retrieve_user(self, db_session):
        """Test saving a user to the database and retrieving it."""
        from sqlalchemy import select

        # Create and save a user
        user = User(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="en",
        )

        db_session.add(user)
        await db_session.flush()

        # Retrieve the user
        stmt = select(User).where(User.telegram_id == 12345)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.telegram_id == 12345
        assert retrieved.username == "testuser"
        assert retrieved.first_name == "Test"
        assert retrieved.last_name == "User"
        assert retrieved.language_code == "en"

    async def test_user_created_at_auto(self, db_session):
        """Test that created_at is set automatically."""
        from sqlalchemy import select

        # Create a user without setting created_at
        user = User(telegram_id=12345)

        db_session.add(user)
        await db_session.commit()

        # Retrieve and check created_at
        stmt = select(User).where(User.telegram_id == 12345)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.created_at is not None
        assert isinstance(retrieved.created_at, datetime.datetime)
        assert retrieved.updated_at is not None
        assert isinstance(retrieved.updated_at, datetime.datetime)

    async def test_user_without_optional_fields(self, db_session):
        """Test saving user with only telegram_id."""
        from sqlalchemy import select

        user = User(telegram_id=99999)

        db_session.add(user)
        await db_session.commit()

        # Retrieve and verify
        stmt = select(User).where(User.telegram_id == 99999)
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()

        assert retrieved.telegram_id == 99999
        assert retrieved.username is None
        assert retrieved.first_name is None
        assert retrieved.last_name is None
        assert retrieved.language_code is None
