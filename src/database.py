"""Управление подключением к базе данных."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from src.models import Base, User


class DatabaseManager:
    """
    Управляет подключением к базе данных и сессиями.

    Предоставляет асинхронный движок и фабрику сессий для работы с БД.
    """

    def __init__(self, database_url: str, logger: logging.Logger) -> None:
        """
        Инициализация менеджера БД.

        Args:
            database_url: URL для подключения к базе данных.
            logger: Логгер для событий.
        """
        self._engine = create_async_engine(database_url, echo=False)
        self._async_session_factory = sessionmaker(  # type: ignore[call-overload]
            self._engine, expire_on_commit=False, class_=AsyncSession
        )
        self._logger = logger
        self._logger.info(f"DatabaseManager initialized for URL: {database_url}")

    async def init_db(self) -> None:
        """
        Инициализирует базу данных, создавая все таблицы.

        Используется для создания схемы БД, если она еще не существует.
        В production рекомендуется использовать Alembic для миграций.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self._logger.info("Database schema initialized (if not already present)")

    def create_session(self) -> AsyncSession:
        """
        Создает новую асинхронную сессию БД.

        Returns:
            AsyncSession: Новая сессия для работы с БД
        """
        session: AsyncSession = self._async_session_factory()
        return session

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Предоставляет асинхронную сессию БД.

        Используется как async context manager для управления жизненным циклом сессии.
        """
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
                self._logger.debug("Database session closed")

    async def close(self) -> None:
        """Закрывает соединение с базой данных."""
        await self._engine.dispose()
        self._logger.info("Database connection pool disposed")

    async def upsert_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        """
        Создает нового пользователя или обновляет существующего (upsert).

        Args:
            telegram_id: Telegram ID пользователя
            username: Username пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            language_code: Код языка пользователя

        Returns:
            User: Созданный или обновленный объект пользователя
        """
        async with self.get_session() as session:
            # Ищем существующего пользователя
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем существующего пользователя
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.language_code = language_code
                self._logger.debug(f"Updated user: telegram_id={telegram_id}")
            else:
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                )
                session.add(user)
                self._logger.info(f"Created new user: telegram_id={telegram_id}")

            await session.commit()
            await session.refresh(user)
            return user
