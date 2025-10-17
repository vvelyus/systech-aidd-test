"""Интерфейс для сборщика статистики диалогов."""

from abc import ABC, abstractmethod

from src.api.models import Period, StatsResponse


class StatCollector(ABC):
    """Интерфейс для сборщика статистики диалогов."""

    @abstractmethod
    async def get_stats(self, period: Period) -> StatsResponse:
        """
        Получить статистику за указанный период.

        Args:
            period: Период для статистики (day/week/month)

        Returns:
            StatsResponse: Полная статистика для дашборда
        """
        pass
