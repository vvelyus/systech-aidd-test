"""Pydantic модели для API статистики."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Period(str, Enum):
    """Период для статистики."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ChatMode(str, Enum):
    """Режим работы чата."""

    NORMAL = "normal"
    ADMIN = "admin"


class MessageRole(str, Enum):
    """Роль отправителя сообщения."""

    USER = "user"
    ASSISTANT = "assistant"


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": {
                    "total_messages": 1250,
                    "total_messages_change": 12.5,
                    "active_users": 45,
                    "active_users_change": -5.2,
                    "avg_dialog_length": 8.3,
                    "avg_dialog_length_change": 3.1,
                    "messages_per_day": 125.0,
                    "messages_per_day_change": 15.8,
                },
                "activity_timeline": [
                    {
                        "date": "2025-10-10",
                        "user_messages": 65,
                        "bot_messages": 58,
                        "total": 123,
                    }
                ],
                "top_users": [
                    {
                        "user_id": 100001,
                        "username": "user1",
                        "first_name": "Иван",
                        "message_count": 150,
                        "last_activity": "2025-10-17T10:30:00",
                    }
                ],
                "recent_dialogs": [
                    {
                        "user_id": 200001,
                        "username": "user1",
                        "first_name": "Петр",
                        "last_message": "Привет! Как дела?",
                        "message_count": 12,
                        "last_activity": "2025-10-17T10:30:00",
                    }
                ],
            }
        }
    )

    summary: SummaryStats
    activity_timeline: list[TimelinePoint]
    top_users: list[UserActivity]
    recent_dialogs: list[DialogPreview]


class ChatMessage(BaseModel):
    """Сообщение чата."""

    id: str = Field(..., description="Уникальный ID сообщения")
    user_session_id: str = Field(..., description="ID сессии пользователя")
    content: str = Field(..., description="Содержание сообщения")
    role: MessageRole = Field(..., description="Роль отправителя")
    mode: ChatMode = Field(..., description="Режим чата")
    sql_query: str | None = Field(None, description="SQL запрос (для админ-режима)")
    created_at: str = Field(..., description="Дата создания (ISO формат)")


class TextToSqlRequest(BaseModel):
    """Запрос на конвертацию вопроса в SQL."""

    question: str = Field(..., description="Вопрос на естественном языке")
    context: dict | None = Field(None, description="Дополнительный контекст")


class TextToSqlResponse(BaseModel):
    """Результат конвертации вопроса в SQL."""

    sql: str = Field(..., description="Сгенерированный SQL запрос")
    explanation: str = Field(..., description="Объяснение запроса")
    is_cached: bool = Field(False, description="Был ли результат получен из кеша")
    error: str | None = Field(None, description="Ошибка если возникла при генерации")


class SuggestedQuestion(BaseModel):
    """Рекомендуемый вопрос для чата."""

    text: str = Field(..., description="Текст вопроса")
    mode: ChatMode = Field(..., description="Для какого режима вопрос")


class PaginatedResponse(BaseModel):
    """Paginated ответ для истории чата."""

    items: list[ChatMessage] = Field(..., description="Массив элементов")
    total: int = Field(..., description="Всего элементов")
    offset: int = Field(..., description="Текущее смещение")
    limit: int = Field(..., description="Использованный лимит")
    hasMore: bool = Field(..., description="Есть ли еще элементы")
