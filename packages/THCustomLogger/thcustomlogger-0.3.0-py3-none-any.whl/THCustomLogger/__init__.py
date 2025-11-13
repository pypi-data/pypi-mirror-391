"""
THCustomLogger - A custom logging package with multiline formatting and rate limiting.

This package provides enhanced logging capabilities with:
- Colorized console output
- Multiline message formatting
- Rate limiting to prevent log spam
- Git integration for commit tracking
- Configurable log rotation
"""

from __future__ import annotations

from .config import LoggerConfig
from .logger_setup import (
    CustomLogger,
    LoggerFactory,
    MultilineFormatter,
    ColoredMultilineFormatter,
)

get_logger = LoggerFactory.get_logger
configure = LoggerFactory.configure

__version__ = "0.3.0"

__all__ = [
    "LoggerFactory",
    "CustomLogger",
    "LoggerConfig",
    # Formatters for advanced use
    "MultilineFormatter",
    "ColoredMultilineFormatter",
    "get_logger",
    "configure",
]
