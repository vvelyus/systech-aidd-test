"""Тесты для Mock реализации сборщика статистики."""

import pytest

from src.api.mock_stats import MockStatCollector
from src.api.models import Period


@pytest.mark.asyncio
async def test_mock_collector_returns_stats() -> None:
    """Тест генерации статистики Mock реализацией."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    assert stats.summary.total_messages > 0
    assert stats.summary.active_users > 0
    assert len(stats.activity_timeline) == 7  # 7 дней для week
    assert len(stats.top_users) <= 5
    assert len(stats.recent_dialogs) <= 10


@pytest.mark.asyncio
async def test_mock_collector_different_periods() -> None:
    """Тест различных периодов."""
    collector = MockStatCollector()

    day_stats = await collector.get_stats(Period.DAY)
    week_stats = await collector.get_stats(Period.WEEK)
    month_stats = await collector.get_stats(Period.MONTH)

    assert len(day_stats.activity_timeline) == 1
    assert len(week_stats.activity_timeline) == 7
    assert len(month_stats.activity_timeline) == 30


@pytest.mark.asyncio
async def test_mock_top_users_sorted() -> None:
    """Топ пользователей должны быть отсортированы по активности."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    counts = [u.message_count for u in stats.top_users]
    assert counts == sorted(counts, reverse=True)


@pytest.mark.asyncio
async def test_mock_recent_dialogs_sorted() -> None:
    """Последние диалоги должны быть отсортированы по времени."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    # Проверяем, что есть диалоги
    assert len(stats.recent_dialogs) > 0

    # Проверяем, что времена отсортированы по убыванию
    times = [d.last_activity for d in stats.recent_dialogs]
    assert times == sorted(times, reverse=True)


@pytest.mark.asyncio
async def test_mock_summary_has_all_fields() -> None:
    """Проверка наличия всех полей в summary."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    summary = stats.summary
    assert hasattr(summary, "total_messages")
    assert hasattr(summary, "total_messages_change")
    assert hasattr(summary, "active_users")
    assert hasattr(summary, "active_users_change")
    assert hasattr(summary, "avg_dialog_length")
    assert hasattr(summary, "avg_dialog_length_change")
    assert hasattr(summary, "messages_per_day")
    assert hasattr(summary, "messages_per_day_change")


@pytest.mark.asyncio
async def test_mock_timeline_has_required_fields() -> None:
    """Проверка полей в точках временной шкалы."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    assert len(stats.activity_timeline) > 0
    for point in stats.activity_timeline:
        assert point.date
        assert point.user_messages >= 0
        assert point.bot_messages >= 0
        assert point.total == point.user_messages + point.bot_messages
