import os
import logging
from typing import Dict, Any
from pathlib import Path


class LoggerConfig:
    # Default configuration in code
    DEFAULT_CONFIG = {
        'log_level': logging.INFO,
        'date_format': "%Y-%m-%d %H:%M:%S",
        'log_format': "%(asctime)s.%(msecs)03d | %(lineno)3d: %(module)s.%(funcName)-25s | %(levelname)-8s: %(message)s",
        'log_dir': 'logs',
        'file_name_prefix': 'app',
        'console_enabled': True,
        'file_enabled': True,
        'rotation_when': 'midnight',
        'rotation_interval': 1,
        'backup_count': 30,
        'encoding': 'utf-8',
        'console_colors': {
            'DEBUG': 'green',
            'INFO': 'light_white',
            'WARNING': 'light_yellow',
            'ERROR': 'light_red',
            'CRITICAL': 'bold_light_purple',
        }
    }

    def __init__(self):
        self._load_config()
        self._overrides = {}

    def _load_config(self):
        """Load configuration from environment variables with defaults"""
        # Basic settings
        self.log_level = self._get_log_level()
        self.date_format = os.getenv('LOGGER_DATE_FORMAT', self.DEFAULT_CONFIG['date_format'])
        self.log_format = os.getenv('LOGGER_FORMAT', self.DEFAULT_CONFIG['log_format'])
        self.log_dir = os.getenv('LOGGER_DIR', self.DEFAULT_CONFIG['log_dir'])
        self.file_name_prefix = os.getenv('LOGGER_FILE_PREFIX', self.DEFAULT_CONFIG['file_name_prefix'])

        # Enable/disable features
        self.console_enabled = self._parse_bool('LOGGER_CONSOLE_ENABLED',
                                                self.DEFAULT_CONFIG['console_enabled'])
        self.file_enabled = self._parse_bool('LOGGER_FILE_ENABLED',
                                             self.DEFAULT_CONFIG['file_enabled'])

        # Rotation settings
        self.rotation_when = os.getenv('LOGGER_ROTATION_WHEN',
                                       self.DEFAULT_CONFIG['rotation_when'])
        self.rotation_interval = int(os.getenv('LOGGER_ROTATION_INTERVAL',
                                               str(self.DEFAULT_CONFIG['rotation_interval'])))
        self.backup_count = int(os.getenv('LOGGER_BACKUP_COUNT',
                                          str(self.DEFAULT_CONFIG['backup_count'])))

        # File settings
        self.encoding = os.getenv('LOGGER_ENCODING', self.DEFAULT_CONFIG['encoding'])

        # Console colors
        self.console_colors = self._get_console_colors()

    def _get_log_level(self) -> int:
        """Convert string level to logging constant"""
        level_name = os.getenv('LOGGER_LEVEL', 'INFO').upper()
        return getattr(logging, level_name, self.DEFAULT_CONFIG['log_level'])

    @staticmethod
    def _parse_bool(env_var: str, default: bool) -> bool:
        """Parse boolean from environment variable"""
        value = os.getenv(env_var, str(default)).lower()
        return value in ('true', '1', 't', 'y', 'yes')

    def _get_console_colors(self) -> Dict[str, str]:
        """Get console colors with fallback to defaults"""
        try:
            color_env = os.getenv('LOGGER_CONSOLE_COLORS')
            if color_env:
                import json
                return json.loads(color_env)
        except Exception as e:
            print(e)
        return self.DEFAULT_CONFIG['console_colors']

    def update_config(self, **kwargs: Any) -> None:
        """Update configuration programmatically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                self._overrides[key] = value
                setattr(self, key, value)

    def reset(self) -> None:
        """Reset configuration to environment/default values"""
        self._overrides.clear()
        self._load_config()

    def get_log_file_path(self) -> Path:
        """Get the full path to the log file"""
        top_level_dir = Path.cwd()
        while top_level_dir.name != 'src' and top_level_dir != top_level_dir.parent:
            top_level_dir = top_level_dir.parent

        if top_level_dir.name == 'src':
            top_level_dir = top_level_dir.parent
        else:
            top_level_dir = Path.cwd()

        return top_level_dir / self.log_dir / f"{self.file_name_prefix}.log"


    @property
    def as_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {
            'log_level': self.log_level,
            'date_format': self.date_format,
            'log_format': self.log_format,
            'log_dir': self.log_dir,
            'file_name_prefix': self.file_name_prefix,
            'console_enabled': self.console_enabled,
            'file_enabled': self.file_enabled,
            'rotation_when': self.rotation_when,
            'rotation_interval': self.rotation_interval,
            'backup_count': self.backup_count,
            'encoding': self.encoding,
            'console_colors': self.console_colors
        }


if __name__ == "__main__":
    config = LoggerConfig()
