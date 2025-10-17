# Спринт F1: Mock API для дашборда статистики

## Обзор

Создание Mock API для независимой разработки frontend. Реализация endpoint для получения статистики по диалогам с тестовыми данными, проектирование контракта API и интерфейса сборщика статистики.

## Структура реализации

### 1. Добавление зависимостей

**Файл:** `pyproject.toml`

Добавить в секцию `dependencies`:

```toml
"fastapi>=0.110.0",
"uvicorn[standard]>=0.27.0",
```

Команда установки: `make install`

### 2. Создание модуля API статистики

**Структура директорий:**

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app и endpoint
│   ├── models.py        # Pydantic модели для API
│   ├── stats.py         # Интерфейс StatCollector
│   └── mock_stats.py    # Mock реализация
```

### 3. Модели данных API

**Файл:** `src/api/models.py`

Создать Pydantic модели:

```python
from enum import Enum
from pydantic import BaseModel, Field


class Period(str, Enum):
    """Период для статистики."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class SummaryStats(BaseModel):
    """Общая статистика для карточек."""
    total_messages: int = Field(..., description="Всего сообщений")
    total_messages_change: float = Field(..., description="Изменение (%)")
    active_users: int = Field(..., description="Активные пользователи")
    active_users_change: float = Field(..., description="Изменение (%)")
    avg_dialog_length: float = Field(..., description="Средняя длина диалога")
    avg_dialog_length_change: float = Field(..., description="Изменение (%)")
    messages_per_day: float = Field(..., description="Сообщений в день")
    messages_per_day_change: float = Field(..., description="Изменение (%)")


class TimelinePoint(BaseModel):
    """Точка на временной шкале."""
    date: str = Field(..., description="Дата в ISO формате")
    user_messages: int = Field(..., description="Сообщения пользователей")
    bot_messages: int = Field(..., description="Сообщения бота")
    total: int = Field(..., description="Всего сообщений")


class UserActivity(BaseModel):
    """Активность пользователя."""
    user_id: int
    username: str | None = None
    first_name: str | None = None
    message_count: int
    last_activity: str = Field(..., description="Последняя активность (ISO)")


class DialogPreview(BaseModel):
    """Превью диалога."""
    user_id: int
    username: str | None = None
    first_name: str | None = None
    last_message: str = Field(..., description="Превью последнего сообщения")
    message_count: int
    last_activity: str = Field(..., description="Последняя активность (ISO)")


class StatsResponse(BaseModel):
    """Полный ответ API со статистикой."""
    summary: SummaryStats
    activity_timeline: list[TimelinePoint]
    top_users: list[UserActivity]
    recent_dialogs: list[DialogPreview]

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "total_messages": 1250,
                    "total_messages_change": 12.5,
                    "active_users": 45,
                    "active_users_change": -5.2,
                    "avg_dialog_length": 8.3,
                    "avg_dialog_length_change": 3.1,
                    "messages_per_day": 125.0,
                    "messages_per_day_change": 15.8
                },
                # ... примеры других полей
            }
        }
```

### 4. Интерфейс StatCollector

**Файл:** `src/api/stats.py`

```python
from abc import ABC, abstractmethod
from src.api.models import StatsResponse, Period


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
```

### 5. Mock реализация

**Файл:** `src/api/mock_stats.py`

```python
from datetime import datetime, timedelta
import random
from src.api.stats import StatCollector
from src.api.models import (
    StatsResponse, Period, SummaryStats,
    TimelinePoint, UserActivity, DialogPreview
)


class MockStatCollector(StatCollector):
    """Mock реализация сборщика статистики с генерацией тестовых данных."""

    async def get_stats(self, period: Period) -> StatsResponse:
        """Генерирует реалистичные тестовые данные."""
        days = self._get_days_for_period(period)

        return StatsResponse(
            summary=self._generate_summary(),
            activity_timeline=self._generate_timeline(days),
            top_users=self._generate_top_users(),
            recent_dialogs=self._generate_recent_dialogs()
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
            messages_per_day_change=round(random.uniform(-10, 20), 1)
        )

    def _generate_timeline(self, days: int) -> list[TimelinePoint]:
        """Генерирует временной ряд."""
        points = []
        now = datetime.now()

        for i in range(days):
            date = now - timedelta(days=days - i - 1)
            user_msgs = random.randint(40, 80)
            bot_msgs = random.randint(35, 75)

            points.append(TimelinePoint(
                date=date.strftime("%Y-%m-%d"),
                user_messages=user_msgs,
                bot_messages=bot_msgs,
                total=user_msgs + bot_msgs
            ))

        return points

    def _generate_top_users(self) -> list[UserActivity]:
        """Генерирует топ активных пользователей."""
        users = []
        for i in range(10):
            users.append(UserActivity(
                user_id=100000 + i,
                username=f"user{i}" if random.random() > 0.3 else None,
                first_name=f"Пользователь {i}",
                message_count=random.randint(50, 200),
                last_activity=(datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            ))

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
            "Есть вопрос по функционалу"
        ]

        for i in range(10):
            dialogs.append(DialogPreview(
                user_id=200000 + i,
                username=f"user{i}" if random.random() > 0.3 else None,
                first_name=f"Иван {i}",
                last_message=random.choice(messages),
                message_count=random.randint(3, 25),
                last_activity=(datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
            ))

        # Сортируем по последней активности
        dialogs.sort(key=lambda d: d.last_activity, reverse=True)
        return dialogs[:10]
```

### 6. FastAPI приложение

**Файл:** `src/api/main.py`

```python
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import StatsResponse, Period
from src.api.stats import StatCollector
from src.api.mock_stats import MockStatCollector


# Создание FastAPI приложения
app = FastAPI(
    title="SysTech AIDD Stats API",
    description="API для получения статистики по диалогам Telegram-бота",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection для StatCollector
# В будущем здесь можно переключаться между Mock и Real
def get_stat_collector() -> StatCollector:
    """Возвращает текущую реализацию StatCollector."""
    return MockStatCollector()


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Stats API is running"}


@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    period: Period = Query(Period.WEEK, description="Период для статистики")
) -> StatsResponse:
    """
    Получить статистику диалогов за указанный период.

    Args:
        period: Период для статистики (day/week/month)

    Returns:
        StatsResponse: Полная статистика для дашборда
    """
    collector = get_stat_collector()
    return await collector.get_stats(period)
```

### 7. Entrypoint для API

**Файл:** `src/api_server.py` (новый файл в корне src/)

```python
"""Entrypoint для запуска API сервера статистики."""

import uvicorn


def main() -> None:
    """Запуск API сервера."""
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload при разработке
        log_level="info"
    )


if __name__ == "__main__":
    main()
```

### 8. Команды в Makefile

**Файл:** `Makefile`

Добавить в секцию help и новые команды:

```makefile
# API Server commands
api-run:
	uv run python src/api_server.py

api-test:
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/ | python -m json.tool
	@echo "\n"
	@curl -s "http://localhost:8000/stats?period=week" | python -m json.tool

api-docs:
	@echo "API Documentation available at:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"
```

Обновить help:

```makefile
@echo "API Server:"
@echo "  make api-run         - Run stats API server (port 8000)"
@echo "  make api-test        - Test API endpoints with curl"
@echo "  make api-docs        - Show API documentation URLs"
```

### 9. Тесты для API

**Файл:** `tests/test_api_stats.py` (новый файл)

```python
import pytest
from src.api.models import Period
from src.api.mock_stats import MockStatCollector


@pytest.mark.asyncio
async def test_mock_collector_returns_stats():
    """Тест генерации статистики Mock реализацией."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    assert stats.summary.total_messages > 0
    assert stats.summary.active_users > 0
    assert len(stats.activity_timeline) == 7  # 7 дней для week
    assert len(stats.top_users) <= 5
    assert len(stats.recent_dialogs) <= 10


@pytest.mark.asyncio
async def test_mock_collector_different_periods():
    """Тест различных периодов."""
    collector = MockStatCollector()

    day_stats = await collector.get_stats(Period.DAY)
    week_stats = await collector.get_stats(Period.WEEK)
    month_stats = await collector.get_stats(Period.MONTH)

    assert len(day_stats.activity_timeline) == 1
    assert len(week_stats.activity_timeline) == 7
    assert len(month_stats.activity_timeline) == 30


@pytest.mark.asyncio
async def test_mock_top_users_sorted():
    """Топ пользователей должны быть отсортированы по активности."""
    collector = MockStatCollector()
    stats = await collector.get_stats(Period.WEEK)

    counts = [u.message_count for u in stats.top_users]
    assert counts == sorted(counts, reverse=True)
```

**Файл:** `tests/test_api_integration.py` (новый файл)

```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Тестовый клиент FastAPI."""
    return TestClient(app)


def test_root_endpoint(client):
    """Тест health check."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stats_endpoint_default(client):
    """Тест получения статистики с параметрами по умолчанию."""
    response = client.get("/stats")
    assert response.status_code == 200

    data = response.json()
    assert "summary" in data
    assert "activity_timeline" in data
    assert "top_users" in data
    assert "recent_dialogs" in data


@pytest.mark.parametrize("period", ["day", "week", "month"])
def test_stats_endpoint_periods(client, period):
    """Тест различных периодов."""
    response = client.get(f"/stats?period={period}")
    assert response.status_code == 200

    data = response.json()
    expected_length = {"day": 1, "week": 7, "month": 30}[period]
    assert len(data["activity_timeline"]) == expected_length


def test_stats_endpoint_invalid_period(client):
    """Тест с некорректным периодом."""
    response = client.get("/stats?period=invalid")
    assert response.status_code == 422  # Validation error
```

### 10. Документация

**Файл:** `frontend/doc/api-contract.md` (новый файл)

```markdown
# Stats API Contract

## Endpoint

GET /stats?period={day|week|month}

## Response Structure

См. автогенерированную документацию:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Примеры использования

bash
# Получить статистику за неделю
curl "http://localhost:8000/stats?period=week"

# Получить статистику за день
curl "http://localhost:8000/stats?period=day"


## Модели данных

Все модели описаны в `src/api/models.py` с использованием Pydantic.
OpenAPI схема генерируется автоматически.
```

## Порядок выполнения

1. Обновить зависимости в `pyproject.toml` и установить их
2. Создать структуру `src/api/` с файлами моделей
3. Реализовать интерфейс `StatCollector` и `MockStatCollector`
4. Создать FastAPI приложение с endpoint
5. Создать entrypoint `src/api_server.py`
6. Добавить команды в `Makefile`
7. Написать тесты для Mock и API
8. Создать документацию контракта API
9. Запустить API и проверить работу через `/docs`
10. Протестировать через `make api-test`

## Результат

После выполнения спринта получим:

- Работающий Mock API на порту 8000
- Автогенерированную OpenAPI документацию
- Четкий контракт для frontend разработки
- Возможность независимой разработки frontend
- Готовую структуру для перехода на Real реализацию
