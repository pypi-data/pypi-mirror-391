"""Logging utilities for warehouse_core."""

import logging
import os
from logging.handlers import RotatingFileHandler
# Python 3.11+ 不需要从 typing 导入 Optional，使用现代联合类型语法


def configure_logging(
    level: str = "INFO",
    log_file: str | None = None,
    logger_name: str = "warehouse_core",
) -> logging.Logger:
    """Configure default logging for warehouse_core consumers.

    Args:
        level: Logging level name, default "INFO".
        log_file: Optional file path for rotating file handler.
        logger_name: Root logger name to configure.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
