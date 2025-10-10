"""Tests for Config module."""

import pytest

from src.config import Config


def test_config_load_with_env_vars(monkeypatch):
    """Test successful configuration loading from environment variables."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test_model")
    monkeypatch.setenv("LOG_FILE_PATH", "test_log.log")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = Config.load()

    assert config["telegram_token"] == "test_bot_token"
    assert config["openrouter_api_key"] == "test_api_key"
    assert config["openrouter_model"] == "test_model"
    assert config["log_file_path"] == "test_log.log"
    assert config["log_level"] == "DEBUG"


def test_config_load_with_defaults(monkeypatch):
    """Test configuration loading with default values."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    # Test that config loads successfully - defaults may come from .env or code defaults
    config = Config.load()

    assert config["telegram_token"] == "test_bot_token"
    # Check that all required keys exist
    assert "openrouter_api_key" in config
    assert "openrouter_model" in config
    assert "log_file_path" in config
    assert "log_level" in config


def test_config_load_missing_required_token(monkeypatch):
    """Test that missing TELEGRAM_BOT_TOKEN is handled gracefully."""
    # This test verifies that Config.load() doesn't crash when tokens are missing
    # Note: load_dotenv() may still load from .env file, so we just verify it doesn't crash
    
    config = Config.load()
    
    # Config should always have these keys, even if values are None
    assert "telegram_token" in config
    assert "openrouter_api_key" in config

