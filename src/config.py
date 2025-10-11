"""Управление конфигурацией приложения."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(Exception):
    """Ошибка конфигурации приложения."""

    pass


@dataclass(frozen=True)
class Config:
    """Конфигурация приложения."""

    telegram_token: str
    openrouter_api_key: str
    bot_name: str = "SysTech AI Assistant"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    system_prompt: str = "Ты - полезный AI-ассистент. Отвечай кратко и по делу."
    max_context_messages: int = 20
    log_file_path: str = "logs/bot.log"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """
        Загружает конфигурацию из .env файла с валидацией.

        Загружает переменные окружения из .env файла и создает
        immutable объект Config. Выбрасывает ConfigError при отсутствии
        обязательных параметров.

        Returns:
            Config: Immutable объект конфигурации

        Raises:
            ConfigError: Если обязательные параметры не найдены
        """
        # Загружаем .env файл
        load_dotenv()

        # Валидация обязательных параметров
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            raise ConfigError("TELEGRAM_BOT_TOKEN не найден в .env файле!")

        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ConfigError("OPENROUTER_API_KEY не найден в .env файле!")

        # Создаем immutable конфигурацию
        return cls(
            telegram_token=telegram_token,
            openrouter_api_key=openrouter_api_key,
            bot_name=os.getenv("BOT_NAME") or cls.bot_name,
            openrouter_model=os.getenv("OPENROUTER_MODEL") or cls.openrouter_model,
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL") or cls.openrouter_base_url,
            system_prompt=os.getenv("SYSTEM_PROMPT") or cls.system_prompt,
            max_context_messages=int(os.getenv("MAX_CONTEXT_MESSAGES") or cls.max_context_messages),
            log_file_path=os.getenv("LOG_FILE_PATH") or cls.log_file_path,
            log_level=os.getenv("LOG_LEVEL") or cls.log_level,
        )
