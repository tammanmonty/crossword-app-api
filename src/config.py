from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings loaded from the environment variables"""
    env: str = "DEVELOPMENT"


    # DATABASE
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str

    # AWS
    aws_region: str
    secret_name: str = None

    # API
    api_host: str
    api_port: int = 8000
    api_reload: bool = False

    # LOGGING
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json" (if you implement custom formatter later)
    log_file: str = "logs/app.log"  # No "../" - relative to where you run the app
    log_to_file: bool = False

    class Config():
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings():
    """Cache the settings to avoid reloading the .env file multiple times"""
    return Settings()


def clear_settings_cache():
    """Clear the settings cache"""
    get_settings().cache_clear()