"""Управление конфигурацией приложения."""

import os
import warnings

from dotenv import load_dotenv


class Config:
    """Управление конфигурацией приложения из .env файла."""

    @staticmethod
    def load() -> dict:
        """
        Загружает конфигурацию из .env файла.

        Загружает переменные окружения из .env файла и возвращает словарь
        с конфигурацией. Для отсутствующих необязательных параметров
        используются значения по умолчанию. При отсутствии обязательных
        параметров выводятся предупреждения.

        Returns:
            dict: Словарь с конфигурацией приложения
        """
        # Загружаем .env файл
        load_dotenv()

        config = {}

        # Обязательные параметры
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            warnings.warn("TELEGRAM_BOT_TOKEN не найден в .env файле!")
        config["telegram_token"] = telegram_token

        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            warnings.warn("OPENROUTER_API_KEY не найден в .env файле!")
        config["openrouter_api_key"] = openrouter_api_key

        # Параметры с значениями по умолчанию
        config["bot_name"] = os.getenv("BOT_NAME", "SysTech AI Assistant")
        config["openrouter_model"] = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        config["openrouter_base_url"] = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        config["system_prompt"] = os.getenv(
            "SYSTEM_PROMPT", "Ты - полезный AI-ассистент. Отвечай кратко и по делу."
        )
        config["max_context_messages"] = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
        config["log_file_path"] = os.getenv("LOG_FILE_PATH", "logs/bot.log")
        config["log_level"] = os.getenv("LOG_LEVEL", "INFO")

        return config
