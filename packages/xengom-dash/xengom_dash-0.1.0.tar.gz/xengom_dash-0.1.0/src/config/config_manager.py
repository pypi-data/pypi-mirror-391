"""User configuration management for myDash."""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages user configuration files."""

    def __init__(self):
        """Initialize config manager."""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.ini"
        self.config = configparser.ConfigParser()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load existing config or create default
        self.load()

    def _get_config_dir(self) -> Path:
        """Get platform-specific config directory.

        Returns:
            Path to config directory
        """
        if os.name == 'nt':  # Windows
            base_dir = os.getenv('APPDATA', str(Path.home()))
        else:  # Linux/Mac
            base_dir = os.getenv('XDG_CONFIG_HOME', str(Path.home() / '.config'))

        return Path(base_dir) / 'mydash'

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self._create_default_config()

    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config['database'] = {
            'path': './data/mydash.db'
        }

        self.config['openweather'] = {
            'api_key': '',
            'city': 'Seoul',
            'units': 'metric'
        }

        self.config['google'] = {
            'credentials_path': '.credentials.json',
            'token_path': '.token.json'
        }

        self.config['refresh_intervals'] = {
            'system': '5',
            'weather': '1800',
            'calendar': '900',
            'gmail': '300',
            'tasks': '600',
            'stocks': '60'
        }

        self.config['logging'] = {
            'level': 'INFO',
            'file': './data/mydash.log'
        }

        self.config['cache'] = {
            'enabled': 'true',
            'ttl': '3600'
        }

        self.save()

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        """Get configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if not found

        Returns:
            Configuration value or fallback
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if not found

        Returns:
            Integer configuration value or fallback
        """
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if not found

        Returns:
            Boolean configuration value or fallback
        """
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))

    def get_all(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration values.

        Returns:
            Dictionary of all configuration sections and values
        """
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config.clear()
        self._create_default_config()


# Global config manager instance
config_manager = ConfigManager()
