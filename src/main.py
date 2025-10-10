"""Точка входа приложения."""

import asyncio
import sys

from bot import TelegramBot
from config import Config
from logger import setup_logger


async def main():
    """Точка входа приложения."""
    # Загружаем конфигурацию
    config = Config.load()

    # Настраиваем логгер
    logger = setup_logger(config["log_file_path"], config["log_level"])
    logger.info("=" * 50)
    logger.info("Запуск приложения systech-aidd-test")
    logger.info("=" * 50)

    # Проверяем обязательные параметры
    if not config["telegram_token"]:
        logger.error("TELEGRAM_BOT_TOKEN не установлен! Проверьте .env файл")
        sys.exit(1)

    if not config["openrouter_api_key"]:
        logger.warning(
            "OPENROUTER_API_KEY не установлен. "
            "LLM функционал будет недоступен в следующих итерациях."
        )

    # Создаем и запускаем бота
    try:
        bot = TelegramBot(token=config["telegram_token"], logger=logger)
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Приложение остановлено")


if __name__ == "__main__":
    asyncio.run(main())
