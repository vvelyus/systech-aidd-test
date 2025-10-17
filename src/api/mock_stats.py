"""Mock реализация сборщика статистики."""

import random
from datetime import datetime, timedelta

from src.api.models import (
    DialogPreview,
    Period,
    StatsResponse,
    SummaryStats,
    TimelinePoint,
    UserActivity,
)
from src.api.stats import StatCollector


class MockStatCollector(StatCollector):
    """Mock реализация сборщика статистики с генерацией тестовых данных."""

    async def get_stats(self, period: Period) -> StatsResponse:
        """Генерирует реалистичные тестовые данные."""
        days = self._get_days_for_period(period)

        return StatsResponse(
            summary=self._generate_summary(),
            activity_timeline=self._generate_timeline(days),
            top_users=self._generate_top_users(),
            recent_dialogs=self._generate_recent_dialogs(),
        )

    def _get_days_for_period(self, period: Period) -> int:
        """Количество дней для периода."""
        return {"day": 1, "week": 7, "month": 30}[period]

    def _generate_summary(self) -> SummaryStats:
        """Генерирует общую статистику."""
        return SummaryStats(
            total_messages=random.randint(1000, 2000),
            total_messages_change=round(random.uniform(-20, 25), 1),
            active_users=random.randint(30, 60),
            active_users_change=round(random.uniform(-15, 20), 1),
            avg_dialog_length=round(random.uniform(5, 15), 1),
            avg_dialog_length_change=round(random.uniform(-10, 15), 1),
            messages_per_day=round(random.uniform(80, 150), 1),
            messages_per_day_change=round(random.uniform(-10, 20), 1),
        )

    def _generate_timeline(self, days: int) -> list[TimelinePoint]:
        """Генерирует временной ряд."""
        points = []
        now = datetime.now()

        for i in range(days):
            date = now - timedelta(days=days - i - 1)
            user_msgs = random.randint(40, 80)
            bot_msgs = random.randint(35, 75)

            points.append(
                TimelinePoint(
                    date=date.strftime("%Y-%m-%d"),
                    user_messages=user_msgs,
                    bot_messages=bot_msgs,
                    total=user_msgs + bot_msgs,
                )
            )

        return points

    def _generate_top_users(self) -> list[UserActivity]:
        """Генерирует топ активных пользователей."""
        users = []
        for i in range(10):
            users.append(
                UserActivity(
                    user_id=100000 + i,
                    username=f"user{i}" if random.random() > 0.3 else None,
                    first_name=f"Пользователь {i}",
                    message_count=random.randint(50, 200),
                    last_activity=(
                        datetime.now() - timedelta(hours=random.randint(1, 48))
                    ).isoformat(),
                )
            )

        # Сортируем по количеству сообщений
        users.sort(key=lambda u: u.message_count, reverse=True)
        return users[:5]  # Топ 5

    def _generate_recent_dialogs(self) -> list[DialogPreview]:
        """Генерирует последние диалоги."""
        dialogs = []
        messages = [
            "Привет! Как дела?",
            "Спасибо за помощь",
            "Можешь объяснить подробнее?",
            "Отлично работает!",
            "Есть вопрос по функционалу",
        ]

        for i in range(10):
            dialogs.append(
                DialogPreview(
                    user_id=200000 + i,
                    username=f"user{i}" if random.random() > 0.3 else None,
                    first_name=f"Иван {i}",
                    last_message=random.choice(messages),
                    message_count=random.randint(3, 25),
                    last_activity=(
                        datetime.now() - timedelta(hours=random.randint(1, 72))
                    ).isoformat(),
                )
            )

        # Сортируем по последней активности
        dialogs.sort(key=lambda d: d.last_activity, reverse=True)
        return dialogs[:10]
