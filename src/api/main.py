"""FastAPI приложение для API статистики."""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api.mock_stats import MockStatCollector
from src.api.models import Period, StatsResponse
from src.api.stats import StatCollector
from src.api import chat
from src.api.chat_service import ChatService
from src.api.real_stats import RealStatCollector
from src.database import DatabaseManager
from src.llm_client import LLMClient
from src.logger import setup_logger
from src.config import Config

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

# Global services
_logger: logging.Logger | None = None
_db_manager: DatabaseManager | None = None
_llm_client: LLMClient | None = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    global _logger, _db_manager, _llm_client

    try:
        # Load config
        config = Config.from_env()

        # Setup logger
        _logger = setup_logger(config.log_file_path, config.log_level)
        _logger.info("Initializing API services...")

        # Initialize database
        _db_manager = DatabaseManager(database_url=config.database_url, logger=_logger)
        await _db_manager.init_db()

        # Load system prompt
        try:
            system_prompt = config.load_system_prompt()
        except Exception:
            system_prompt = config.system_prompt

        # Initialize LLM client
        _llm_client = LLMClient(
            api_key=config.openrouter_api_key,
            model=config.openrouter_model,
            base_url=config.openrouter_base_url,
            system_prompt=system_prompt,
            logger=_logger,
            context_storage=None,
        )

        # Initialize ChatService
        chat_service = ChatService(
            llm_client=_llm_client,
            db_manager=_db_manager,
            logger=_logger,
            request_timeout=90.0,  # Increased from 60s to 90s for complex queries
            text2sql_timeout=30.0,  # Increased from 5s to 30s for SQL generation
        )

        # Register chat service
        chat.set_chat_service(chat_service, _logger)

        _logger.info("API services initialized successfully")
    except Exception as e:
        if _logger:
            _logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    if _db_manager:
        await _db_manager.close()
    if _logger:
        _logger.info("API services shutdown complete")


# Dependency Injection для StatCollector
def get_stat_collector() -> StatCollector:
    """Возвращает текущую реализацию StatCollector."""
    return RealStatCollector(_db_manager)


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

# Подключение chat endpoints
app.include_router(chat.router)
