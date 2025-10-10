"""Tests for logger module."""

import logging
import os
from pathlib import Path

from src.logger import setup_logger


def test_setup_logger_creates_logger():
    """Test that setup_logger creates a logger with correct name."""
    logger = setup_logger("test_logs/test.log", "INFO")

    assert logger.name == "systech_bot"
    assert logger.level == logging.INFO


def test_setup_logger_creates_log_directory(tmp_path):
    """Test that setup_logger creates logs directory if it doesn't exist."""
    log_path = tmp_path / "logs" / "test.log"

    logger = setup_logger(str(log_path), "INFO")

    assert log_path.parent.exists()
    assert log_path.parent.is_dir()


def test_setup_logger_with_debug_level():
    """Test logger setup with DEBUG log level."""
    logger = setup_logger("test_logs/test.log", "DEBUG")

    assert logger.level == logging.DEBUG


def test_setup_logger_with_warning_level():
    """Test logger setup with WARNING log level."""
    logger = setup_logger("test_logs/test.log", "WARNING")

    assert logger.level == logging.WARNING


def test_setup_logger_with_invalid_level():
    """Test logger setup with invalid log level defaults to INFO."""
    logger = setup_logger("test_logs/test.log", "INVALID")

    # Should default to INFO
    assert logger.level == logging.INFO

