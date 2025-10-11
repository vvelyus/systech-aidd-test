"""Абстракция хранилища контекста диалогов."""

import logging
from typing import Protocol


class ContextStorage(Protocol):
    """Протокол для хранилища контекста диалогов."""

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст пользователя.

        Args:
            user_id: ID пользователя
            role: Роль отправителя (user или assistant)
            content: Текст сообщения
        """
        ...

    def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        ...

    def reset_context(self, user_id: int) -> None:
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

    def add_message(self, user_id: int, role: str, content: str) -> None:
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

    def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Получить контекст для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: Список сообщений в формате [{"role": ..., "content": ...}, ...]
        """
        return self._storage.get(user_id, [])

    def reset_context(self, user_id: int) -> None:
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
