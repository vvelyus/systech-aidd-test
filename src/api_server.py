"""Entrypoint для запуска API сервера статистики."""

import uvicorn


def main() -> None:
    """Запуск API сервера."""
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload при разработке
        log_level="info",
    )


if __name__ == "__main__":
    main()
