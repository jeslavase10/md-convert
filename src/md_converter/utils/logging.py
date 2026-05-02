"""Structured logging for md-convert."""

import logging
import sys
from enum import Enum
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

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
        self._setup_logger()

    def _setup_logger(self):
        """Set up logger with rich handler."""
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level.to_logging_level())
        self._logger.handlers.clear()

        # Rich handler with custom theme
        console = Console(theme=MD_CONVERT_THEME)
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        self._logger.addHandler(handler)

    def set_level(self, level: LogLevel):
        """Change log level dynamically."""
        self.level = level
        self._logger.setLevel(level.to_logging_level())

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


def get_logger(name: str, level: Optional[LogLevel] = None) -> MDConvertLogger:
    """Get or create a logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        MDConvertLogger instance
    """
    global _global_level

    if name not in _loggers:
        effective_level = level or _global_level
        _loggers[name] = MDConvertLogger(name, effective_level)

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
        config: Dict with 'level' key ('debug', 'info', 'warning', 'error')
    """
    level_str = config.get("level", "info")
    try:
        level = LogLevel(level_str.lower())
        set_global_level(level)
    except ValueError:
        pass  # Keep current level


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
