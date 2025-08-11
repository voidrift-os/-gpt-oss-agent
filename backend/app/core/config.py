"""Application settings loaded from environment variables.

This module defines a small ``Settings`` class that centralises all runtime
configuration. It uses Pydantic's ``BaseSettings`` so values can be overridden
via environment variables or an ``.env`` file during development.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl


class Settings(BaseSettings):
    """Central application configuration.
    
    Defaults are provided so that the application and test suite can run even
    when the expected environment variables are not defined. These values can
    be overridden by setting the corresponding variables or by providing an
    ``.env`` file.
    """

    # Security
    secret_key: str = "change-me"
    
    # Database (default to SQLite for local dev/tests; override in prod via env)
    database_url: str = "sqlite+aiosqlite:///./app.db"
    
    # Redis
    redis_url: AnyUrl = "redis://localhost:6379/0"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "Wealth App API"
    allowed_origins: list[str] = []
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Toggle verbose SQLAlchemy logging; overridable via ``DEBUG`` env var.
    debug: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate settings once on import
settings = Settings()
