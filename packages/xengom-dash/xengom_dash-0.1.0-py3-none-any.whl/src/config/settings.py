import os
from pathlib import Path
from dotenv import load_dotenv
from src.config.config_manager import config_manager

# Load environment variables (fallback)
load_dotenv()


def _get_config_value(section: str, key: str, env_key: str, default: str = '') -> str:
    """Get configuration value with priority: user config > env > default.

    Args:
        section: Config section
        key: Config key
        env_key: Environment variable name
        default: Default value

    Returns:
        Configuration value
    """
    # Priority 1: User config file
    value = config_manager.get(section, key)
    if value is not None and value != '':
        return value

    # Priority 2: Environment variable
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value

    # Priority 3: Default value
    return default


def _get_config_int(section: str, key: str, env_key: str, default: int) -> int:
    """Get integer configuration value with priority: user config > env > default.

    Args:
        section: Config section
        key: Config key
        env_key: Environment variable name
        default: Default value

    Returns:
        Integer configuration value
    """
    # Priority 1: User config file
    value = config_manager.get_int(section, key, fallback=None)
    if value is not None:
        return value

    # Priority 2: Environment variable
    env_value = os.getenv(env_key)
    if env_value is not None:
        try:
            return int(env_value)
        except ValueError:
            pass

    # Priority 3: Default value
    return default


def _get_config_bool(section: str, key: str, env_key: str, default: bool) -> bool:
    """Get boolean configuration value with priority: user config > env > default.

    Args:
        section: Config section
        key: Config key
        env_key: Environment variable name
        default: Default value

    Returns:
        Boolean configuration value
    """
    # Priority 1: User config file
    value = config_manager.get(section, key)
    if value is not None and value != '':
        return value.lower() in ('true', '1', 'yes', 'on')

    # Priority 2: Environment variable
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value.lower() in ('true', '1', 'yes', 'on')

    # Priority 3: Default value
    return default


class Settings:
    """Application settings with priority: user config > env > defaults."""

    # Project root
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # Database
    DATABASE_PATH = _get_config_value('database', 'path', 'DATABASE_PATH', './data/mydash.db')

    # OpenWeather API
    OPENWEATHER_API_KEY = _get_config_value('openweather', 'api_key', 'OPENWEATHER_API_KEY', '')
    OPENWEATHER_CITY = _get_config_value('openweather', 'city', 'OPENWEATHER_CITY', 'Seoul')
    OPENWEATHER_UNITS = _get_config_value('openweather', 'units', 'OPENWEATHER_UNITS', 'metric')
    WEATHER_CITY = OPENWEATHER_CITY  # Alias for easier access

    # Update intervals (seconds)
    REFRESH_INTERVAL_SYSTEM = _get_config_int('refresh_intervals', 'system', 'REFRESH_INTERVAL_SYSTEM', 5)
    REFRESH_INTERVAL_WEATHER = _get_config_int('refresh_intervals', 'weather', 'REFRESH_INTERVAL_WEATHER', 1800)
    REFRESH_INTERVAL_CALENDAR = _get_config_int('refresh_intervals', 'calendar', 'REFRESH_INTERVAL_CALENDAR', 900)
    REFRESH_INTERVAL_GMAIL = _get_config_int('refresh_intervals', 'gmail', 'REFRESH_INTERVAL_GMAIL', 300)
    REFRESH_INTERVAL_TASKS = _get_config_int('refresh_intervals', 'tasks', 'REFRESH_INTERVAL_TASKS', 600)
    REFRESH_INTERVAL_STOCKS = _get_config_int('refresh_intervals', 'stocks', 'REFRESH_INTERVAL_STOCKS', 60)

    # Google OAuth
    GOOGLE_CREDENTIALS_PATH = _get_config_value('google', 'credentials_path', 'GOOGLE_CREDENTIALS_PATH', '.credentials.json')
    GOOGLE_TOKEN_PATH = _get_config_value('google', 'token_path', 'GOOGLE_TOKEN_PATH', '.token.json')
    GOOGLE_SCOPES = os.getenv('GOOGLE_SCOPES', '').split(',')

    # Logging
    LOG_LEVEL = _get_config_value('logging', 'level', 'LOG_LEVEL', 'INFO')
    LOG_FILE = _get_config_value('logging', 'file', 'LOG_FILE', './data/mydash.log')

    # Cache
    CACHE_ENABLED = _get_config_bool('cache', 'enabled', 'CACHE_ENABLED', True)
    CACHE_TTL = _get_config_int('cache', 'ttl', 'CACHE_TTL', 3600)

    @classmethod
    def reload(cls):
        """Reload settings from config file."""
        config_manager.load()
        # Re-initialize all settings
        cls.DATABASE_PATH = _get_config_value('database', 'path', 'DATABASE_PATH', './data/mydash.db')
        cls.OPENWEATHER_API_KEY = _get_config_value('openweather', 'api_key', 'OPENWEATHER_API_KEY', '')
        cls.OPENWEATHER_CITY = _get_config_value('openweather', 'city', 'OPENWEATHER_CITY', 'Seoul')
        cls.OPENWEATHER_UNITS = _get_config_value('openweather', 'units', 'OPENWEATHER_UNITS', 'metric')
        cls.WEATHER_CITY = cls.OPENWEATHER_CITY
        cls.REFRESH_INTERVAL_SYSTEM = _get_config_int('refresh_intervals', 'system', 'REFRESH_INTERVAL_SYSTEM', 5)
        cls.REFRESH_INTERVAL_WEATHER = _get_config_int('refresh_intervals', 'weather', 'REFRESH_INTERVAL_WEATHER', 1800)
        cls.REFRESH_INTERVAL_CALENDAR = _get_config_int('refresh_intervals', 'calendar', 'REFRESH_INTERVAL_CALENDAR', 900)
        cls.REFRESH_INTERVAL_GMAIL = _get_config_int('refresh_intervals', 'gmail', 'REFRESH_INTERVAL_GMAIL', 300)
        cls.REFRESH_INTERVAL_TASKS = _get_config_int('refresh_intervals', 'tasks', 'REFRESH_INTERVAL_TASKS', 600)
        cls.REFRESH_INTERVAL_STOCKS = _get_config_int('refresh_intervals', 'stocks', 'REFRESH_INTERVAL_STOCKS', 60)
        cls.GOOGLE_CREDENTIALS_PATH = _get_config_value('google', 'credentials_path', 'GOOGLE_CREDENTIALS_PATH', '.credentials.json')
        cls.GOOGLE_TOKEN_PATH = _get_config_value('google', 'token_path', 'GOOGLE_TOKEN_PATH', '.token.json')
        cls.LOG_LEVEL = _get_config_value('logging', 'level', 'LOG_LEVEL', 'INFO')
        cls.LOG_FILE = _get_config_value('logging', 'file', 'LOG_FILE', './data/mydash.log')
        cls.CACHE_ENABLED = _get_config_bool('cache', 'enabled', 'CACHE_ENABLED', True)
        cls.CACHE_TTL = _get_config_int('cache', 'ttl', 'CACHE_TTL', 3600)


settings = Settings()
