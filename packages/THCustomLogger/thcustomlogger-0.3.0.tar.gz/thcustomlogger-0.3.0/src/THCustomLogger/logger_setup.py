from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

import colorlog

from THCustomLogger.config import LoggerConfig


class LoggerFactory:
    _loggers: Dict[str, "CustomLogger"] = {}
    _lock = threading.Lock()
    _config = LoggerConfig()

    @classmethod
    def get_config(cls) -> LoggerConfig:
        """Get logger configuration instance"""
        return cls._config

    @classmethod
    def configure(cls, **kwargs):
        """Configure logger settings"""
        cls._config.update_config(**kwargs)
        # Optionally recreate existing loggers with new config
        with cls._lock:
            for name, logger in cls._loggers.items():
                cls._setup_logger(name, recreate=True)

    @classmethod
    def _setup_logger(cls, name: str, recreate: bool = False) -> logging.Logger:
        config = cls._config

        os.makedirs(config.get_log_file_path().parent, exist_ok=True)

        logger = logging.getLogger(name)

        if recreate or not logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Set up console handler if enabled
            if config.console_enabled:
                console_handler = colorlog.StreamHandler()
                console_handler.setFormatter(ColoredMultilineFormatter(
                    "%(log_color)s" + config.log_format,
                    datefmt=config.date_format,
                    log_colors=config.console_colors
                ))
                logger.addHandler(console_handler)

            # Set up the file handler if enabled
            if config.file_enabled:
                file_handler = TimedRotatingFileHandler(
                    filename=config.get_log_file_path(),
                    when=config.rotation_when,
                    interval=config.rotation_interval,
                    backupCount=config.backup_count,
                    encoding=config.encoding,
                    delay=False
                )
                file_handler.setFormatter(MultilineFormatter(
                    fmt=config.log_format,
                    datefmt=config.date_format
                ))
                logger.addHandler(file_handler)

            logger.setLevel(config.log_level)

        return logger

    @classmethod
    def get_logger(cls, name: str) -> "CustomLogger":
        """Get or create a logger with the given name"""
        with cls._lock:
            logging.setLoggerClass(CustomLogger)
            if name not in cls._loggers:
                logger = cls._setup_logger(name)
                cls._loggers[name] = logger
            return cls._loggers[name]


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._message_cache = {}
        self._cache_lock = threading.Lock()
        # Configuration for rate limiting
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_count = 10  # max occurrences within window
        self.rate_limit_enabled = True

    @staticmethod
    def _get_message_key(level, msg, args):
        """Generate a unique key for the log message"""
        try:
            formatted_msg = msg % args if args else msg
        except:
            formatted_msg = str(msg)
        return level, formatted_msg

    def _should_log(self, level, msg, args):
        """Check if the message should be logged based on rate limiting"""
        if not self.rate_limit_enabled:
            return True

        key = self._get_message_key(level, msg, args)
        current_time = time.time()

        with self._cache_lock:
            if key not in self._message_cache:
                self._message_cache[key] = {
                    'count': 1,
                    'first_seen': current_time,
                    'last_logged': current_time,
                    'suppressed_count': 0
                }
                return True

            cache_entry = self._message_cache[key]
            time_since_first = current_time - cache_entry['first_seen']

            # Reset the window if enough time has passed
            if time_since_first > self.rate_limit_window:
                # Log summary of suppressed messages if any
                if cache_entry['suppressed_count'] > 0:
                    self._log_suppression_summary(level, cache_entry['suppressed_count'], msg)

                cache_entry['count'] = 1
                cache_entry['first_seen'] = current_time
                cache_entry['last_logged'] = current_time
                cache_entry['suppressed_count'] = 0
                return True

            # Increment count
            cache_entry['count'] += 1

            # Check if we've exceeded the limit
            if cache_entry['count'] <= self.rate_limit_max_count:
                cache_entry['last_logged'] = current_time
                return True

            # Exceeded limit - suppress this message
            cache_entry['suppressed_count'] += 1

            # Log a warning every N suppressed messages
            if cache_entry['suppressed_count'] % 100 == 0:
                self._log_suppression_warning(level, cache_entry['suppressed_count'])

            return False

    def _log_suppression_summary(self, level, suppressed_count, original_msg):
        """Log a summary of suppressed messages"""
        summary_msg = f"[RATE LIMIT] Suppressed {suppressed_count} duplicate log message(s) in the last {self.rate_limit_window}s"
        # Log without rate limiting to avoid infinite recursion
        old_enabled = self.rate_limit_enabled
        self.rate_limit_enabled = False
        super().log(logging.WARNING, summary_msg)
        self.rate_limit_enabled = old_enabled

    def _log_suppression_warning(self, level, suppressed_count):
        """Log a warning that messages are being suppressed"""
        warning_msg = f"[RATE LIMIT] {suppressed_count} messages suppressed and counting..."
        old_enabled = self.rate_limit_enabled
        self.rate_limit_enabled = False
        super().log(logging.WARNING, warning_msg)
        self.rate_limit_enabled = old_enabled

    def configure_rate_limit(self, enabled=True, window_seconds=60, max_count=10):
        """Configure rate limiting parameters"""
        self.rate_limit_enabled = enabled
        self.rate_limit_window = window_seconds
        self.rate_limit_max_count = max_count
        self._message_cache.clear()

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """Override _log method to add rate limiting"""
        if self._should_log(level, msg, args):
            super()._log(level, msg, args, exc_info=exc_info, extra=extra,
                         stack_info=stack_info, stacklevel=stacklevel)

    def get_commit_hash(self):
        """Get the current git commit hash"""
        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT
            ).decode("utf-8").strip()
            return commit_hash
        except subprocess.CalledProcessError as e:
            self.error(f"Error getting commit hash: {e.output.decode('utf-8')}")
            return "unknown"

    def get_latest_tag(self):
        """Get the latest git tag"""
        try:
            latest_tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.STDOUT
            ).decode("utf-8").strip()
            return latest_tag
        except subprocess.CalledProcessError as e:
            self.error(f"Error getting latest tag: {e.output.decode('utf-8')}")
            return "unknown"


class MultilineFormatter(logging.Formatter):
    def format(self, record):
        original = super().format(record)
        message = record.getMessage()
        prefix, _, _ = original.partition(message)
        return _format_multiline(record, original, message, prefix)


class ColoredMultilineFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        original = super().format(record)
        message = record.getMessage()
        prefix, _, _ = original.partition(message)
        return _format_multiline(record, original, message, prefix, color_offset=5)


def _format_multiline(record, original, message, prefix, color_offset=0):
    indent = ' ' * (len(prefix) - color_offset)

    color_start = prefix[:color_offset] if color_offset > 0 else ''
    color_reset = '\x1b[0m' if color_offset > 0 else ''

    msg_break = getattr(record, 'msg_break', None)
    if msg_break is not None:
        msg_break = msg_break * (len(prefix) - color_offset)
        msg_break = f"{color_start}{msg_break}{color_reset}"

    no_indent = getattr(record, 'no_indent', False)
    if no_indent or '\n' not in message:
        if msg_break is not None:
            return original + '\n' + msg_break
        return original

    lines = message.splitlines()
    indented_message = lines[0] + '\n' + '\n'.join(indent + line for line in lines[1:])
    formatted = prefix + indented_message

    if msg_break is not None:
        return formatted + '\n' + msg_break
    return formatted


def main(logger):
    logger.info(f"Done.", extra={'msg_break': '*'})
    logger.info(f"Done.\n----------", extra={'no_indent': True})
    logger.info(f"Done.\nfffffffffff", extra={'msg_break': '/', 'no_indent': True})

    logger.debug('debug message')
    logger.info('hello world')
    logger.warning('Oh No')
    logger.error('Error')
    logger.critical('Critical')
    logger.info(f"Commit hash: {logger.get_commit_hash()}")

    logger.info(f"Commit hash: {logger.get_commit_hash()}\nLatest tag:{logger.get_latest_tag()}")


def example(logger):
    try:
        1 / 0
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    logger_ex = LoggerFactory.get_logger(__name__)

    LoggerFactory.configure(log_level=logging.DEBUG)

    logger_ex.info(f"Commit hash: {logger_ex.get_commit_hash()}")

    main(logger_ex)
    example(logger_ex)

    logger = LoggerFactory.get_logger(__name__)

    logger.info("Message with custom break", extra={'msg_break': '*'})
    logger.info("No indent message\nSecond line", extra={'no_indent': True})
