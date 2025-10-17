"""FastAPI приложение для API статистики."""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.mock_stats import MockStatCollector
from src.api.models import Period, StatsResponse
from src.api.stats import StatCollector
from src.api import chat

# Создание FastAPI приложения
app = FastAPI(
    title="SysTech AIDD Stats API",
    description="API для получения статистики по диалогам Telegram-бота",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    period: Period = Query(Period.WEEK, description="Период для статистики"),
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
from src.api import chat

# Подключение chat endpoints
app.include_router(chat.router)

