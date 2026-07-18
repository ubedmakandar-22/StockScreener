"""Logging configuration and utilities."""

import logging
import logging.handlers
import os
from typing import Optional

from config import Config


class LoggerSetup:
    """Centralized logging configuration."""

    _loggers: dict[str, logging.Logger] = {}

    @staticmethod
    def setup_logger(
        name: str,
        config: Config,
        level: Optional[str] = None,
    ) -> logging.Logger:
        """
        Setup and return a logger instance.

        Args:
            name: Logger name (usually __name__).
            config: Configuration object.
            level: Log level override.

        Returns:
            Configured logger instance.
        """
        if name in LoggerSetup._loggers:
            return LoggerSetup._loggers[name]

        logger = logging.getLogger(name)
        log_level = level or config.LOG_LEVEL
        logger.setLevel(getattr(logging, log_level))

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(getattr(logging, log_level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))

        # Formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        LoggerSetup._loggers[name] = logger
        return logger
