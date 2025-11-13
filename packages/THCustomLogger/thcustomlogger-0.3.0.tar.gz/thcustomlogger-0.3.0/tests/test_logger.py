import logging
import os
import shutil
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from THCustomLogger import LoggerFactory, CustomLogger, LoggerConfig


@pytest.fixture
def clean_env():
    """Fixture to clean environment variables"""
    env_vars = [
        'LOGGER_LEVEL', 'LOGGER_DATE_FORMAT', 'LOGGER_FORMAT',
        'LOGGER_DIR', 'LOGGER_FILE_PREFIX', 'LOGGER_CONSOLE_ENABLED',
        'LOGGER_FILE_ENABLED', 'LOGGER_ROTATION_WHEN',
        'LOGGER_ROTATION_INTERVAL', 'LOGGER_BACKUP_COUNT',
        'LOGGER_ENCODING', 'LOGGER_CONSOLE_COLORS'
    ]
    original_env = {}
    for var in env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]

    yield

    # Restore original environment
    for var, value in original_env.items():
        os.environ[var] = value


@pytest.fixture
def temp_log_dir():
    """Fixture to create and clean up temporary log directory"""
    temp_dir = tempfile.mkdtemp()
    LoggerFactory._loggers.clear()
    LoggerFactory.configure(
        log_dir=temp_dir,
        file_name_prefix='test',
        console_enabled=False,
        file_enabled=True,
        log_level=logging.DEBUG
    )

    yield temp_dir

    # Clean up handlers before removing directory
    for logger in LoggerFactory._loggers.values():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    LoggerFactory._loggers.clear()


@pytest.fixture
def logger(temp_log_dir):
    """Fixture to provide a configured logger with unique name per test"""
    import uuid
    unique_name = f'test_logger_{uuid.uuid4().hex[:8]}'
    return LoggerFactory.get_logger(unique_name)


class TestLoggerConfig:
    """Test suite for LoggerConfig class"""

    def test_default_config(self, clean_env):
        """Test that default configuration is loaded correctly"""
        config = LoggerConfig()
        assert config.log_level == logging.INFO
        assert config.log_dir == 'logs'
        assert config.file_name_prefix == 'app'
        assert config.console_enabled is True
        assert config.file_enabled is True
        assert config.rotation_when == 'midnight'
        assert config.rotation_interval == 1
        assert config.backup_count == 30
        assert config.encoding == 'utf-8'

    def test_config_from_environment(self, clean_env):
        """Test configuration loading from environment variables"""
        os.environ['LOGGER_LEVEL'] = 'DEBUG'
        os.environ['LOGGER_DIR'] = 'test_logs'
        os.environ['LOGGER_FILE_PREFIX'] = 'test'
        os.environ['LOGGER_CONSOLE_ENABLED'] = 'false'

        config = LoggerConfig()
        assert config.log_level == logging.DEBUG
        assert config.log_dir == 'test_logs'
        assert config.file_name_prefix == 'test'
        assert config.console_enabled is False

    def test_update_config(self, clean_env):
        """Test runtime configuration updates"""
        config = LoggerConfig()
        config.update_config(log_level=logging.WARNING, log_dir='custom_logs')

        assert config.log_level == logging.WARNING
        assert config.log_dir == 'custom_logs'

    def test_reset_config(self, clean_env):
        """Test configuration reset"""
        config = LoggerConfig()
        config.update_config(log_level=logging.WARNING)
        assert config.log_level == logging.WARNING

        config.reset()
        assert config.log_level == logging.INFO

    def test_config_as_dict(self, clean_env):
        """Test configuration dictionary export"""
        config = LoggerConfig()
        config_dict = config.as_dict

        assert isinstance(config_dict, dict)
        assert 'log_level' in config_dict
        assert 'log_dir' in config_dict
        assert 'console_enabled' in config_dict

    @pytest.mark.parametrize("env_value,expected", [
        ("true", True),
        ("True", True),
        ("1", True),
        ("t", True),
        ("yes", True),
        ("false", False),
        ("False", False),
        ("0", False),
        ("no", False),
    ])
    def test_parse_bool(self, clean_env, env_value, expected):
        """Test boolean parsing from environment variables"""
        os.environ['LOGGER_CONSOLE_ENABLED'] = env_value
        config = LoggerConfig()
        assert config.console_enabled is expected


class TestLoggerFactory:
    """Test suite for LoggerFactory class"""

    def test_get_logger(self, temp_log_dir):
        """Test logger creation"""
        logger = LoggerFactory.get_logger('test_logger')

        assert isinstance(logger, CustomLogger)
        assert logger.name == 'test_logger'

    def test_logger_singleton(self, temp_log_dir):
        """Test that same logger instance is returned for same name"""
        logger1 = LoggerFactory.get_logger('test_logger')
        logger2 = LoggerFactory.get_logger('test_logger')

        assert logger1 is logger2

    def test_multiple_loggers(self, temp_log_dir):
        """Test creation of multiple different loggers"""
        logger1 = LoggerFactory.get_logger('logger1')
        logger2 = LoggerFactory.get_logger('logger2')

        assert logger1 is not logger2
        assert len(LoggerFactory._loggers) == 2

    def test_configure_updates_existing_loggers(self, temp_log_dir):
        """Test that configuration updates affect existing loggers"""
        logger = LoggerFactory.get_logger('test_logger')
        original_level = logger.level

        # Change to a different level
        new_level = logging.WARNING if original_level == logging.DEBUG else logging.DEBUG
        LoggerFactory.configure(log_level=new_level)

        assert logger.level == new_level
        assert logger.level != original_level

    def test_get_config(self):
        """Test getting configuration instance"""
        config = LoggerFactory.get_config()
        assert isinstance(config, LoggerConfig)

    def test_thread_safe_logger_creation(self, temp_log_dir):
        """Test that logger creation is thread-safe"""
        loggers = []

        def create_logger():
            logger = LoggerFactory.get_logger('concurrent_logger')
            loggers.append(logger)

        threads = [threading.Thread(target=create_logger) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All should be the same instance
        assert all(logger is loggers[0] for logger in loggers)


class TestCustomLogger:
    """Test suite for CustomLogger class"""

    def test_basic_logging(self, logger, temp_log_dir):
        """Test basic logging functionality"""
        # Disable rate limiting for basic logging test
        logger.configure_rate_limit(enabled=False)

        logger.info("Test message")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Flush all handlers
        for handler in logger.handlers:
            handler.flush()

        # Check that log file was created
        log_file = Path(temp_log_dir) / 'test.log'
        assert log_file.exists(), f"Log file not found at {log_file}"

        # Verify content
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Test message" in content

    @pytest.mark.parametrize("level,method", [
        (logging.DEBUG, "debug"),
        (logging.INFO, "info"),
        (logging.WARNING, "warning"),
        (logging.ERROR, "error"),
        (logging.CRITICAL, "critical"),
    ])
    def test_logging_levels(self, logger, temp_log_dir, level, method):
        """Test all logging levels"""
        # Disable rate limiting for this test
        logger.configure_rate_limit(enabled=False)

        message = f"Test {method} message"
        getattr(logger, method)(message)

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert message in content

    def test_rate_limiting(self, logger, temp_log_dir):
        """Test rate limiting functionality"""
        logger.configure_rate_limit(enabled=True, window_seconds=2, max_count=3)

        # Log the same message multiple times
        for i in range(5):
            logger.info("RateLimitTest1")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        # Read log file
        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        # Should have 3 "RateLimitTest1" logs (max_count=3)
        message_count = content.count("RateLimitTest1")
        assert message_count == 3, f"Expected 3 messages, got {message_count}"

    def test_rate_limiting_window_reset(self, logger, temp_log_dir):
        """Test that rate limiting window resets after timeout"""
        logger.configure_rate_limit(enabled=True, window_seconds=1, max_count=2)

        # Log messages - first 2 should succeed, third should be suppressed
        logger.info("WindowReset1")
        logger.info("WindowReset1")
        logger.info("WindowReset1")  # This should be suppressed

        # Flush to ensure first batch is written
        for handler in logger.handlers:
            handler.flush()

        # Wait for window to reset
        time.sleep(1.5)

        # Log again - should succeed because window reset
        logger.info("WindowReset1")
        logger.info("WindowReset1")  # Should succeed - new window

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        # Read log file
        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        # Should have 2 messages in first window + 2 after reset + suppression summary = 4 + summary
        message_count = content.count("WindowReset1")
        assert message_count == 4, f"Expected 4 messages, got {message_count}"
        # Should also have suppression summary for the 1 suppressed message
        assert "RATE LIMIT" in content
        assert "Suppressed 1 duplicate log message" in content

    def test_rate_limiting_disabled(self, logger, temp_log_dir):
        """Test logging with rate limiting disabled"""
        logger.configure_rate_limit(enabled=False)

        # Log the same message multiple times
        for i in range(5):
            logger.info("Repeated message")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        # Read log file
        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        # All messages should be logged
        message_count = content.count("Repeated message")
        assert message_count == 5

    def test_rate_limiting_different_messages(self, logger, temp_log_dir):
        """Test that rate limiting is per-message"""
        logger.configure_rate_limit(enabled=True, window_seconds=10, max_count=2)

        # Log different messages
        logger.info("Message A")
        logger.info("Message A")
        logger.info("Message B")
        logger.info("Message B")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        # Both messages should appear twice
        assert content.count("Message A") == 2
        assert content.count("Message B") == 2

    @patch('subprocess.check_output')
    def test_get_commit_hash_success(self, mock_subprocess, logger):
        """Test getting git commit hash successfully"""
        mock_subprocess.return_value = b'abc123def456\n'

        commit_hash = logger.get_commit_hash()
        assert commit_hash == 'abc123def456'

    @patch('subprocess.check_output')
    def test_get_commit_hash_failure(self, mock_subprocess, logger):
        """Test getting git commit hash when git is not available"""
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, 'git', b'error')

        commit_hash = logger.get_commit_hash()
        assert commit_hash == 'unknown'

    @patch('subprocess.check_output')
    def test_get_latest_tag_success(self, mock_subprocess, logger):
        """Test getting latest git tag successfully"""
        mock_subprocess.return_value = b'v1.0.0\n'

        tag = logger.get_latest_tag()
        assert tag == 'v1.0.0'

    @patch('subprocess.check_output')
    def test_get_latest_tag_failure(self, mock_subprocess, logger):
        """Test getting latest git tag when no tags exist"""
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, 'git', b'error')

        tag = logger.get_latest_tag()
        assert tag == 'unknown'

    def test_thread_safety(self, logger, temp_log_dir):
        """Test that logger is thread-safe"""
        results = []

        def log_messages(thread_id):
            try:
                for i in range(10):
                    logger.info(f"Thread {thread_id} - Message {i}")
                results.append(True)
            except Exception:
                results.append(False)

        threads = [threading.Thread(target=log_messages, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All threads should complete successfully
        assert all(results)
        assert len(results) == 5

    def test_configure_rate_limit(self, logger):
        """Test rate limit configuration"""
        logger.configure_rate_limit(enabled=True, window_seconds=30, max_count=5)

        assert logger.rate_limit_enabled is True
        assert logger.rate_limit_window == 30
        assert logger.rate_limit_max_count == 5


class TestLoggerHandlers:
    """Test suite for logger handlers configuration"""

    def test_console_handler_only(self):
        """Test logger with only console handler"""
        temp_dir = tempfile.mkdtemp()
        try:
            LoggerFactory._loggers.clear()
            LoggerFactory.configure(
                log_dir=temp_dir,
                console_enabled=True,
                file_enabled=False
            )
            logger = LoggerFactory.get_logger('console_logger')

            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
            assert not any(isinstance(h, logging.handlers.TimedRotatingFileHandler)
                           for h in logger.handlers)
        finally:
            for logger in LoggerFactory._loggers.values():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            shutil.rmtree(temp_dir)
            LoggerFactory._loggers.clear()

    def test_file_handler_only(self):
        """Test logger with only file handler"""
        temp_dir = tempfile.mkdtemp()
        try:
            LoggerFactory._loggers.clear()
            LoggerFactory.configure(
                log_dir=temp_dir,
                console_enabled=False,
                file_enabled=True
            )
            logger = LoggerFactory.get_logger('file_logger')

            assert not any(isinstance(h, logging.StreamHandler) and
                           not isinstance(h, logging.handlers.TimedRotatingFileHandler)
                           for h in logger.handlers)
        finally:
            for logger in LoggerFactory._loggers.values():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            shutil.rmtree(temp_dir)
            LoggerFactory._loggers.clear()

    def test_both_handlers(self):
        """Test logger with both console and file handlers"""
        temp_dir = tempfile.mkdtemp()
        try:
            LoggerFactory._loggers.clear()
            LoggerFactory.configure(
                log_dir=temp_dir,
                console_enabled=True,
                file_enabled=True
            )
            logger = LoggerFactory.get_logger('both_logger')

            # Should have at least 1 handler
            assert len(logger.handlers) >= 1
        finally:
            for logger in LoggerFactory._loggers.values():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            shutil.rmtree(temp_dir)
            LoggerFactory._loggers.clear()

    def test_log_file_creation(self, temp_log_dir):
        """Test that log file is created"""
        logger = LoggerFactory.get_logger('test_logger')
        logger.info("Test message")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        assert log_file.exists()

        with open(log_file, 'r') as f:
            content = f.read()
        assert "Test message" in content

    def test_no_handlers(self):
        """Test logger with no handlers"""
        temp_dir = tempfile.mkdtemp()
        try:
            LoggerFactory._loggers.clear()
            LoggerFactory.configure(
                log_dir=temp_dir,
                console_enabled=False,
                file_enabled=False
            )
            logger = LoggerFactory.get_logger('no_handler_logger')

            # Logger should exist but have no handlers
            assert isinstance(logger, CustomLogger)
            assert len(logger.handlers) == 0
        finally:
            shutil.rmtree(temp_dir)
            LoggerFactory._loggers.clear()


class TestMultilineFormatting:
    """Test suite for multiline message formatting"""

    def test_multiline_message(self, logger, temp_log_dir):
        """Test logging multiline messages"""
        logger.info("Line 1\nLine 2\nLine 3")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content

    def test_message_with_break(self, logger, temp_log_dir):
        """Test logging with message break"""
        logger.info("Test message", extra={'msg_break': '*'})

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Test message" in content
        assert "*" in content

    def test_message_no_indent(self, logger, temp_log_dir):
        """Test logging without indentation"""
        logger.info("Line 1\nLine 2", extra={'no_indent': True})

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Line 1" in content
        assert "Line 2" in content

    @pytest.mark.parametrize("break_char", ['*', '-', '=', '#', '/'])
    def test_different_break_characters(self, logger, temp_log_dir, break_char):
        """Test different break characters"""
        logger.info("Test", extra={'msg_break': break_char})

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert break_char in content

    def test_combined_multiline_and_break(self, logger, temp_log_dir):
        """Test multiline message with break"""
        logger.info("Line 1\nLine 2", extra={'msg_break': '='})

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Line 1" in content
        assert "Line 2" in content
        assert "=" in content


class TestLoggerIntegration:
    """Integration tests for the logger system"""

    def test_full_logging_workflow(self, temp_log_dir):
        """Test complete logging workflow"""
        # Configure logger
        LoggerFactory.configure(
            log_level=logging.DEBUG,
            console_enabled=False,
            file_enabled=True
        )

        # Get logger and log messages
        logger = LoggerFactory.get_logger('integration_test')
        logger.debug("Debug info")
        logger.info("Application started")
        logger.warning("Warning message")
        logger.error("Error occurred")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        # Verify log file
        log_file = Path(temp_log_dir) / 'test.log'
        assert log_file.exists()

        with open(log_file, 'r') as f:
            content = f.read()

        assert "Debug info" in content
        assert "Application started" in content
        assert "Warning message" in content
        assert "Error occurred" in content

    def test_reconfiguration(self, temp_log_dir):
        """Test logger reconfiguration"""
        logger = LoggerFactory.get_logger('reconfig_test')

        # Initial config
        logger.info("Message 1")

        # Reconfigure
        LoggerFactory.configure(log_level=logging.ERROR)

        # This should not be logged
        logger.info("Message 2")

        # This should be logged
        logger.error("Message 3")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        log_file = Path(temp_log_dir) / 'test.log'
        with open(log_file, 'r') as f:
            content = f.read()

        assert "Message 1" in content
        assert "Message 2" not in content
        assert "Message 3" in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
