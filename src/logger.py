"""Настройка логирования для приложения."""

import logging
from pathlib import Path


def setup_logger(log_file: str, log_level: str = "INFO") -> logging.Logger:
    """
    Настраивает логирование в файл и консоль.

    Создает логгер с выводом в файл и консоль. Автоматически создает
    директорию для лог-файла, если она не существует.

    Args:
        log_file: Путь к файлу логов
        log_level: Уровень логирования (INFO, WARNING, ERROR и т.д.)

    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов, если её нет
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Настраиваем форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Настраиваем логгер
    logger = logging.getLogger("systech_bot")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Очищаем существующие обработчики (если есть)
    logger.handlers.clear()

    # Обработчик для файла
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
