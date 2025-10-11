"""Точка входа приложения."""

import asyncio
import sys

from src.bot import TelegramBot
from src.config import Config, ConfigError
from src.context_storage import InMemoryContextStorage
from src.llm_client import LLMClient
from src.logger import setup_logger


async def main() -> None:
    """Точка входа приложения."""
    # Загружаем конфигурацию с валидацией
    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)

    # Настраиваем логгер
    logger = setup_logger(config.log_file_path, config.log_level)
    logger.info("=" * 50)
    logger.info("Starting systech-aidd-test application")
    logger.info("=" * 50)

    # Загружаем системный промпт из файла
    try:
        system_prompt = config.load_system_prompt()
        logger.info(f"Loaded system prompt from {config.system_prompt_file}")
    except ConfigError as e:
        logger.error(f"Failed to load system prompt: {e}")
        logger.warning("Using default system prompt from config")
        system_prompt = config.system_prompt

    # Создаем хранилище контекста
    context_storage = InMemoryContextStorage(
        max_messages=config.max_context_messages,
        max_users=1000,
        logger=logger,
    )

    # Создаем LLM клиент
    try:
        llm_client = LLMClient(
            api_key=config.openrouter_api_key,
            model=config.openrouter_model,
            base_url=config.openrouter_base_url,
            system_prompt=system_prompt,
            logger=logger,
            context_storage=context_storage,
        )
        logger.info("LLM client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLMClient: {e}", exc_info=True)
        logger.warning("Bot will run in echo mode without LLM")
        llm_client = None

    # Создаем и запускаем бота
    try:
        bot = TelegramBot(
            token=config.telegram_token,
            logger=logger,
            system_prompt=system_prompt,
            llm_client=llm_client,
            bot_name=config.bot_name,
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
