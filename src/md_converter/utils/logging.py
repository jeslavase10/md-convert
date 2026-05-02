"""Structured logging for md-convert."""

import logging
import sys
from enum import Enum
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from logging.handlers import RotatingFileHandler

# Custom theme for md-convert output
MD_CONVERT_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "green",
    "debug": "dim",
})


class LogLevel(Enum):
    """Log levels for md-convert."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    def to_logging_level(self) -> int:
        """Convert to logging module level."""
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
        }
        return mapping[self]


class MDConvertLogger:
    """Logger for md-convert with rich output support.

    Usage:
        from md_converter.utils.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Starting conversion")
        logger.debug("Processing file: {path}", path=input_file)
        logger.warning("Mermaid CLI not found, using fallback")
        logger.error("Failed to render PDF")
    """

    _logger_cache = {}

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self._file_handler = None
        self._setup_logger()

    def _setup_logger(self):
        """Set up logger with rich handler and optional file handler."""
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level.to_logging_level())
        self._logger.handlers.clear()

        # Rich handler with custom theme (console output)
        console = Console(theme=MD_CONVERT_THEME)
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        self._logger.addHandler(handler)

        # Add file handler if configured
        if self._file_handler:
            self._logger.addHandler(self._file_handler)

    def set_level(self, level: LogLevel):
        """Change log level dynamically."""
        self.level = level
        self._logger.setLevel(level.to_logging_level())

    def add_file_handler(
        self,
        path: Path,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        level: LogLevel = LogLevel.DEBUG,
    ):
        """Add rotating file handler for file logging.

        Args:
            path: Path to log file
            max_bytes: Max size per log file before rotation
            backup_count: Number of backup files to keep
            level: Minimum log level for file output
        """
        # Create directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create rotating handler
        handler = RotatingFileHandler(
            str(path),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setLevel(level.to_logging_level())

        # Simple formatter (no colors for file)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        self._file_handler = handler
        self._logger.addHandler(handler)

    def debug(self, msg: str, **kwargs):
        """Log debug message."""
        self._logger.debug(msg, **{k: v for k, v in kwargs.items() if v is not None})

    def info(self, msg: str, **kwargs):
        """Log info message."""
        self._logger.info(msg, **{k: v for k, v in kwargs.items() if v is not None})

    def warning(self, msg: str, **kwargs):
        """Log warning message."""
        self._logger.warning(msg, **{k: v for k, v in kwargs.items() if v is not None})

    def error(self, msg: str, **kwargs):
        """Log error message."""
        self._logger.error(msg, **{k: v for k, v in kwargs.items() if v is not None})

    def success(self, msg: str, **kwargs):
        """Log success message (custom level)."""
        self._logger.info(f"[green]✓[/green] {msg}", **{
            k: v for k, v in kwargs.items() if v is not None
        })


# Global logger registry
_loggers = {}
_global_level = LogLevel.INFO
_log_file_path = None


def get_logger(name: str, level: Optional[LogLevel] = None) -> MDConvertLogger:
    """Get or create a logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        MDConvertLogger instance
    """
    global _global_level, _log_file_path

    if name not in _loggers:
        effective_level = level or _global_level
        _loggers[name] = MDConvertLogger(name, effective_level)

        # Add file handler if configured globally
        if _log_file_path:
            _loggers[name].add_file_handler(_log_file_path)

    return _loggers[name]


def set_global_level(level: LogLevel):
    """Set global log level for all loggers."""
    global _global_level
    _global_level = level
    for logger in _loggers.values():
        logger.set_level(level)


def configure_logging(config: dict):
    """Configure logging from config dict.

    Args:
        config: Dict with keys:
            - level: 'debug', 'info', 'warning', 'error'
            - log_file: Path to log file (enables file logging)
            - log_max_bytes: Max size per file (default 10MB)
            - log_backup_count: Number of backups (default 5)
    """
    global _log_file_path

    level_str = config.get("level", "info")
    try:
        level = LogLevel(level_str.lower())
        set_global_level(level)
    except ValueError:
        pass  # Keep current level

    # Configure file logging if path provided
    log_file = config.get("log_file")
    if log_file:
        log_path = Path(log_file)
        max_bytes = config.get("log_max_bytes", 10 * 1024 * 1024)
        backup_count = config.get("log_backup_count", 5)
        _log_file_path = log_path

        # Add file handler to all existing loggers
        for logger in _loggers.values():
            logger.add_file_handler(log_path, max_bytes, backup_count)


# Convenience console for simple output
console = Console(theme=MD_CONVERT_THEME)


def log_info(msg: str, **kwargs):
    """Quick info log."""
    get_logger("md-convert").info(msg, **kwargs)


def log_warning(msg: str, **kwargs):
    """Quick warning log."""
    get_logger("md-convert").warning(msg, **kwargs)


def log_error(msg: str, **kwargs):
    """Quick error log."""
    get_logger("md-convert").error(msg, **kwargs)


def log_success(msg: str, **kwargs):
    """Quick success log."""
    get_logger("md-convert").success(msg, **kwargs)


def log_debug(msg: str, **kwargs):
    """Quick debug log."""
    get_logger("md-convert").debug(msg, **kwargs)
