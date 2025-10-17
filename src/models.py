"""SQLAlchemy модели для базы данных."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


class User(Base):
    """
    Модель для хранения данных пользователей Telegram.

    Attributes:
        telegram_id: Уникальный Telegram ID пользователя
        username: Telegram username (может отсутствовать)
        first_name: Имя пользователя
        last_name: Фамилия пользователя (может отсутствовать)
        language_code: Код языка пользователя
        created_at: Дата и время первого обращения
        updated_at: Дата и время последнего обновления данных
    """

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        """
        Строковое представление модели для отладки.

        Returns:
            str: Читаемое представление объекта User
        """
        return (
            f"<User(telegram_id={self.telegram_id}, username='{self.username}', "
            f"first_name='{self.first_name}', last_name='{self.last_name}', "
            f"created_at={self.created_at})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразование модели в словарь.

        Returns:
            dict: Словарь с полями модели
        """
        return {
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    """
    Модель для хранения сообщений диалога.

    Attributes:
        id: Уникальный идентификатор сообщения
        user_id: Telegram ID пользователя
        role: Роль отправителя ('user' или 'assistant')
        content: Текст сообщения
        length: Длина сообщения в символах
        created_at: Дата и время создания
        is_deleted: Флаг soft delete (False = активно, True = удалено)
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.current_timestamp()
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0", index=True
    )

    def __init__(self, **kwargs: Any) -> None:
        """
        Инициализация модели с default значениями.

        Args:
            **kwargs: Поля модели
        """
        if "is_deleted" not in kwargs:
            kwargs["is_deleted"] = False
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """
        Строковое представление модели для отладки.

        Returns:
            str: Читаемое представление объекта Message
        """
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"<Message(id={self.id}, user_id={self.user_id}, role='{self.role}', "
            f"length={self.length}, created_at={self.created_at}, "
            f"is_deleted={self.is_deleted}, content='{content_preview}')>"
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразование модели в словарь.

        Returns:
            dict: Словарь с полями модели
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "length": self.length,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_deleted": self.is_deleted,
        }
