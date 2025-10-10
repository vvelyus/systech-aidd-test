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
    logger.info("Starting systech-aidd-test application")
    logger.info("=" * 50)

    # Проверяем обязательные параметры
    if not config["telegram_token"]:
        logger.error("TELEGRAM_BOT_TOKEN is not set! Check your .env file")
        sys.exit(1)

    if not config["openrouter_api_key"]:
        logger.warning(
            "OPENROUTER_API_KEY is not set. "
            "LLM functionality will be unavailable in next iterations."
        )

    # Создаем и запускаем бота
    try:
        bot = TelegramBot(token=config["telegram_token"], logger=logger)
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received stop signal (Ctrl+C)")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application stopped")


if __name__ == "__main__":
    asyncio.run(main())
