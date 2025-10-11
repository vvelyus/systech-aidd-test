"""Точка входа приложения."""

import asyncio
import sys

from bot import TelegramBot
from config import Config
from llm_client import LLMClient
from logger import setup_logger


async def main() -> None:
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

    # Создаем LLM клиент если есть API key
    llm_client = None
    if config["openrouter_api_key"]:
        try:
            llm_client = LLMClient(
                api_key=config["openrouter_api_key"],
                model=config["openrouter_model"],
                base_url=config["openrouter_base_url"],
                system_prompt=config["system_prompt"],
                logger=logger,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLMClient: {e}", exc_info=True)
            logger.warning("Bot will run in echo mode without LLM")
    else:
        logger.warning("OPENROUTER_API_KEY is not set. Bot will run in echo mode without LLM")

    # Создаем и запускаем бота
    try:
        bot = TelegramBot(
            token=config["telegram_token"],
            logger=logger,
            llm_client=llm_client,
            bot_name=config["bot_name"],
        )
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
