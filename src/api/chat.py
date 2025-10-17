"""API endpoints для чата."""

from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
import logging

from src.api.models import ChatMode, TextToSqlRequest
from src.api.chat_service import ChatService
from src.database import DatabaseManager
from src.llm_client import LLMClient

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global instances - will be set during app initialization
_chat_service: ChatService | None = None
_logger: logging.Logger | None = None


def set_chat_service(service: ChatService, logger: logging.Logger) -> None:
    """Set the global chat service instance."""
    global _chat_service, _logger
    _chat_service = service
    _logger = logger


def get_chat_service() -> ChatService:
    """Get the current chat service instance."""
    if _chat_service is None:
        raise RuntimeError("ChatService not initialized")
    return _chat_service


@router.post("/message")
async def chat_message(
    message: str = Query(..., description="Сообщение от пользователя"),
    session_id: str = Query(..., description="ID сессии чата"),
    mode: ChatMode = Query(ChatMode.NORMAL, description="Режим чата (normal/admin)"),
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """
    Обрабатывает сообщение пользователя и возвращает потоковый ответ (SSE).

    Args:
        message: Текст сообщения
        session_id: ID сессии чата
        mode: Режим работы (normal или admin)
        service: ChatService для обработки

    Returns:
        StreamingResponse с SSE событиями

    Example:
        POST /api/chat/message?message=Привет&session_id=uuid&mode=normal
    """
    async def generate():
        import json
        try:
            async for chunk in service.process_message(message, session_id, mode):
                # Properly escape the JSON string
                escaped_chunk = json.dumps(chunk, ensure_ascii=False)
                yield f'data: {{"content": {escaped_chunk}}}\n\n'
        except Exception as e:
            error_msg = str(e)[:100]
            escaped_error = json.dumps(error_msg, ensure_ascii=False)
            yield f'data: {{"error": {escaped_error}}}\n\n'
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
async def get_chat_history(
    session_id: str = Query(..., description="ID сессии чата"),
    limit: int = Query(50, ge=1, le=200, description="Максимальное количество сообщений"),
    offset: int = Query(0, ge=0, description="Смещение от начала (для pagination)"),
) -> dict:
    """
    Получает историю сообщений для сессии с поддержкой pagination.

    Args:
        session_id: ID сессии чата
        limit: Максимальное количество сообщений (1-200, по умолчанию 50)
        offset: Смещение для pagination (по умолчанию 0)

    Returns:
        PaginatedResponse с сообщениями:
        {
            "items": [...],      # Массив сообщений
            "total": 100,        # Всего сообщений в сессии
            "hasMore": true,     # Есть ли еще сообщения
            "offset": 0,         # Текущее смещение
            "limit": 50          # Использованный лимит
        }

    Example:
        GET /api/chat/history?session_id=uuid&limit=50&offset=0
    """
    # TODO: Интегрировать ChatService для получения истории
    # Временный mock ответ
    total_count = 100
    has_more = (offset + limit) < total_count

    return {
        "items": [],  # Will be populated by ChatService
        "total": total_count,
        "hasMore": has_more,
        "offset": offset,
        "limit": limit
    }


@router.post("/debug/sql")
async def debug_sql(
    request: TextToSqlRequest,
) -> dict:
    """
    Для админ-режима: показать сгенерированный SQL запрос без выполнения.

    Args:
        request: Запрос на конвертацию (question + context)

    Returns:
        TextToSqlResponse с SQL запросом и объяснением

    Example:
        POST /api/chat/debug/sql
        {
            "question": "Сколько сообщений было отправлено на этой неделе?",
            "context": {}
        }
    """
    # TODO: Интегрировать Text2SqlConverter для генерации SQL
    return {
        "sql": "SELECT COUNT(*) as total FROM messages WHERE created_at > date('now', '-7 days');",
        "explanation": "Получить количество сообщений за последние 7 дней",
    }


@router.post("/session")
async def create_chat_session(
    user_id: int = Query(..., description="ID пользователя"),
    mode: ChatMode = Query(ChatMode.NORMAL, description="Режим чата"),
) -> dict:
    """
    Создает новую сессию чата.

    Args:
        user_id: ID пользователя (Telegram ID)
        mode: Начальный режим чата

    Returns:
        ID новой сессии и информация о ней

    Example:
        POST /api/chat/session?user_id=123456&mode=normal
    """
    # TODO: Интегрировать ChatService для создания сессии
    import uuid
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "user_id": user_id,
        "mode": mode.value,
    }
