"""Интеграционные тесты для FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Тестовый клиент FastAPI."""
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Тест health check."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stats_endpoint_default(client: TestClient) -> None:
    """Тест получения статистики с параметрами по умолчанию."""
    response = client.get("/stats")
    assert response.status_code == 200

    data = response.json()
    assert "summary" in data
    assert "activity_timeline" in data
    assert "top_users" in data
    assert "recent_dialogs" in data


@pytest.mark.parametrize("period", ["day", "week", "month"])
def test_stats_endpoint_periods(client: TestClient, period: str) -> None:
    """Тест различных периодов."""
    response = client.get(f"/stats?period={period}")
    assert response.status_code == 200

    data = response.json()
    expected_length = {"day": 1, "week": 7, "month": 30}[period]
    assert len(data["activity_timeline"]) == expected_length


def test_stats_endpoint_invalid_period(client: TestClient) -> None:
    """Тест с некорректным периодом."""
    response = client.get("/stats?period=invalid")
    assert response.status_code == 422  # Validation error


def test_stats_response_structure(client: TestClient) -> None:
    """Проверка структуры ответа API."""
    response = client.get("/stats?period=week")
    assert response.status_code == 200

    data = response.json()

    # Проверка summary
    assert "total_messages" in data["summary"]
    assert "active_users" in data["summary"]
    assert "avg_dialog_length" in data["summary"]
    assert "messages_per_day" in data["summary"]

    # Проверка activity_timeline
    assert len(data["activity_timeline"]) == 7
    for point in data["activity_timeline"]:
        assert "date" in point
        assert "user_messages" in point
        assert "bot_messages" in point
        assert "total" in point

    # Проверка top_users
    assert len(data["top_users"]) <= 5
    for user in data["top_users"]:
        assert "user_id" in user
        assert "message_count" in user
        assert "last_activity" in user

    # Проверка recent_dialogs
    assert len(data["recent_dialogs"]) <= 10
    for dialog in data["recent_dialogs"]:
        assert "user_id" in dialog
        assert "last_message" in dialog
        assert "message_count" in dialog
        assert "last_activity" in dialog


def test_openapi_docs_available(client: TestClient) -> None:
    """Проверка доступности OpenAPI документации."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema(client: TestClient) -> None:
    """Проверка OpenAPI схемы."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "SysTech AIDD Stats API"
    assert "/stats" in schema["paths"]
