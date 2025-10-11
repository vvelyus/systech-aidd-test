"""Tests for Config module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import Config, ConfigError


def test_config_from_env_with_all_vars(monkeypatch):
    """Test successful configuration loading with all environment variables."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        monkeypatch.setenv("OPENROUTER_MODEL", "test_model")
        monkeypatch.setenv("BOT_NAME", "Test Bot")
        monkeypatch.setenv("LOG_FILE_PATH", "test_log.log")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "30")

        config = Config.from_env()

        assert config.telegram_token == "test_bot_token"
        assert config.openrouter_api_key == "test_api_key"
        assert config.openrouter_model == "test_model"
        assert config.bot_name == "Test Bot"
        assert config.log_file_path == "test_log.log"
        assert config.log_level == "DEBUG"
        assert config.max_context_messages == 30


def test_config_from_env_with_defaults(monkeypatch):
    """Test configuration loading with default values for optional parameters."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        # Clear all optional env vars
        monkeypatch.delenv("BOT_NAME", raising=False)
        monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
        monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
        monkeypatch.delenv("SYSTEM_PROMPT", raising=False)
        monkeypatch.delenv("MAX_CONTEXT_MESSAGES", raising=False)
        monkeypatch.delenv("LOG_FILE_PATH", raising=False)
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        config = Config.from_env()

        # Required fields
        assert config.telegram_token == "test_bot_token"
        assert config.openrouter_api_key == "test_api_key"

        # Optional fields with defaults
        assert config.bot_name == "SysTech AI Assistant"
        assert config.openrouter_model == "anthropic/claude-3.5-sonnet"
        assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert config.system_prompt == "Ты - полезный AI-ассистент. Отвечай кратко и по делу."
        assert config.max_context_messages == 20
        assert config.log_file_path == "logs/bot.log"
        assert config.log_level == "INFO"


def test_config_raises_error_missing_telegram_token(monkeypatch):
    """Test that ConfigError is raised when TELEGRAM_BOT_TOKEN is missing."""
    with patch("src.config.load_dotenv"):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")

        with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN"):
            Config.from_env()


def test_config_raises_error_missing_openrouter_api_key(monkeypatch):
    """Test that ConfigError is raised when OPENROUTER_API_KEY is missing."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        with pytest.raises(ConfigError, match="OPENROUTER_API_KEY"):
            Config.from_env()


def test_config_raises_error_missing_both_required(monkeypatch):
    """Test that ConfigError is raised when both required fields are missing."""
    with patch("src.config.load_dotenv"):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN"):
            Config.from_env()


def test_config_immutability(monkeypatch):
    """Test that Config is immutable (frozen dataclass)."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")

        config = Config.from_env()

        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            config.telegram_token = "new_token"  # type: ignore[misc]


# Tests for Config.load_system_prompt()


def test_config_load_system_prompt_success(monkeypatch):
    """Test successful loading of system prompt from existing file."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        monkeypatch.setenv("SYSTEM_PROMPT_FILE", "prompts/system_prompt.txt")

        config = Config.from_env()

        # Act
        prompt = config.load_system_prompt()

        # Assert
        assert prompt
        assert "Технический консультант" in prompt
        assert len(prompt) > 50


def test_config_load_system_prompt_file_not_found(monkeypatch):
    """Test that ConfigError is raised when prompt file does not exist."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        monkeypatch.setenv("SYSTEM_PROMPT_FILE", "prompts/nonexistent.txt")

        config = Config.from_env()

        # Act & Assert
        with pytest.raises(ConfigError, match="System prompt file not found"):
            config.load_system_prompt()


def test_config_load_system_prompt_empty_file(monkeypatch):
    """Test that ConfigError is raised when prompt file is empty."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")

        # Create temporary empty file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name
            # Write nothing (empty file)

        try:
            monkeypatch.setenv("SYSTEM_PROMPT_FILE", temp_file)
            config = Config.from_env()

            # Act & Assert
            with pytest.raises(ConfigError, match="System prompt file is empty"):
                config.load_system_prompt()
        finally:
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)


def test_config_load_system_prompt_with_custom_path(monkeypatch):
    """Test loading system prompt from custom path."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")

        # Create temporary file with custom content
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name
            f.write("Custom test prompt content")

        try:
            monkeypatch.setenv("SYSTEM_PROMPT_FILE", temp_file)
            config = Config.from_env()

            # Act
            prompt = config.load_system_prompt()

            # Assert
            assert prompt == "Custom test prompt content"
        finally:
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)


def test_config_from_env_with_system_prompt_file(monkeypatch):
    """Test that system_prompt_file field is correctly loaded from env."""
    with patch("src.config.load_dotenv"):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        monkeypatch.setenv("SYSTEM_PROMPT_FILE", "custom/path/prompt.txt")

        config = Config.from_env()

        # Assert
        assert config.system_prompt_file == "custom/path/prompt.txt"
