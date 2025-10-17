"""Абстракция хранилища контекста диалогов."""

import logging
from typing import Protocol

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Message


class ContextStorage(Protocol):
    """Протокол для хранилища контекста диалогов."""

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст пользователя.

        Args:
            user_id: ID пользователя
            role: Роль отправителя (user или assistant)
            content: Текст сообщения
        """
        ...

    async def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        ...

    async def reset_context(self, user_id: int) -> None:
        """
        Очистить контекст диалога для пользователя.

        Args:
            user_id: ID пользователя
        """
        ...


class InMemoryContextStorage:
    """
    Хранилище контекста в памяти.

    Сохраняет историю сообщений для каждого пользователя в памяти процесса.
    Поддерживает ограничение по количеству сообщений для предотвращения
    переполнения памяти.
    """

    def __init__(
        self,
        max_messages: int = 20,
        max_users: int = 1000,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Инициализация хранилища.

        Args:
            max_messages: Максимальное количество сообщений на пользователя
            max_users: Максимальное количество пользователей
            logger: Логгер для событий (опционально)
        """
        self._storage: dict[int, list[dict[str, str]]] = {}
        self._max_messages = max_messages
        self._max_users = max_users
        self._logger = logger

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст с ограничением.

        Если количество сообщений превышает max_messages,
        оставляет только последние max_messages сообщений.

        Args:
            user_id: ID пользователя
            role: Роль отправителя (user или assistant)
            content: Текст сообщения
        """
        # Проверка лимита пользователей
        if user_id not in self._storage and len(self._storage) >= self._max_users:
            # Очищаем самого старого пользователя (простая стратегия)
            oldest_user = next(iter(self._storage))
            del self._storage[oldest_user]
            if self._logger:
                self._logger.warning(
                    f"Max users limit reached ({self._max_users}). "
                    f"Removed context for user_id={oldest_user}"
                )

        # Инициализируем список для нового пользователя
        if user_id not in self._storage:
            self._storage[user_id] = []

        # Добавляем сообщение
        self._storage[user_id].append({"role": role, "content": content})

        # Ограничение: последние max_messages сообщений
        if len(self._storage[user_id]) > self._max_messages:
            self._storage[user_id] = self._storage[user_id][-self._max_messages :]
            if self._logger:
                self._logger.debug(
                    f"Context trimmed to {self._max_messages} messages for user_id={user_id}"
                )

    async def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        return self._storage.get(user_id, [])

    async def reset_context(self, user_id: int) -> None:
        """
        Очистить контекст диалога для пользователя.

        Args:
            user_id: ID пользователя
        """
        if user_id in self._storage:
            del self._storage[user_id]
            if self._logger:
                self._logger.info(f"Context reset for user_id={user_id}")
        else:
            if self._logger:
                self._logger.info(f"No context to reset for user_id={user_id}")

    def get_user_count(self) -> int:
        """
        Получить количество пользователей в хранилище.

        Returns:
            int: Количество пользователей
        """
        return len(self._storage)

    def clear_all(self) -> None:
        """Очистить все данные из хранилища."""
        self._storage.clear()
        if self._logger:
            self._logger.info("All context data cleared")


class DatabaseContextStorage:
    """
    Хранилище контекста в базе данных.

    Сохраняет историю сообщений в БД с использованием SQLAlchemy.
    Поддерживает soft delete и ограничение по количеству сообщений.
    """

    def __init__(
        self,
        session: AsyncSession,
        max_messages: int = 20,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Инициализация хранилища.

        Args:
            session: Async SQLAlchemy session
            max_messages: Максимальное количество сообщений на пользователя
            logger: Логгер для событий (опционально)
        """
        self._session = session
        self._max_messages = max_messages
        self._logger = logger

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст.

        Автоматически вычисляет длину сообщения.

        Args:
            user_id: ID пользователя
            role: Роль отправителя (user или assistant)
            content: Текст сообщения
        """
        import datetime

        message = Message(
            user_id=user_id,
            role=role,
            content=content,
            length=len(content),
            created_at=datetime.datetime.now(),
            is_deleted=False,
        )
        self._session.add(message)
        await self._session.commit()

        if self._logger:
            self._logger.debug(
                f"Added message for user_id={user_id}, role={role}, length={len(content)}"
            )

    async def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Возвращает последние N активных сообщений в хронологическом порядке.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        # Выбираем последние N активных сообщений
        stmt = (
            select(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)  # noqa: E712
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(self._max_messages)
        )

        result = await self._session.execute(stmt)
        messages = result.scalars().all()

        # Разворачиваем, чтобы получить хронологический порядок
        messages_reversed = list(reversed(messages))

        context = [{"role": msg.role, "content": msg.content} for msg in messages_reversed]

        if self._logger:
            self._logger.debug(f"Retrieved {len(context)} messages for user_id={user_id}")

        return context

    async def reset_context(self, user_id: int) -> None:
        """
        Очистить контекст диалога для пользователя (soft delete).

        Помечает все активные сообщения пользователя как удаленные.

        Args:
            user_id: ID пользователя
        """
        stmt = (
            update(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)  # noqa: E712
            .values(is_deleted=True)
        )

        await self._session.execute(stmt)
        await self._session.commit()

        if self._logger:
            self._logger.info(f"Context reset for user_id={user_id}")

    async def close(self) -> None:
        """Закрыть сессию БД."""
        await self._session.close()
        if self._logger:
            self._logger.info("Database session closed")
