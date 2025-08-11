from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Defaults are provided so that the application and test suite can run
    even when the expected environment variables are not defined. These
    values can be overridden by setting the corresponding variables or by
    providing a `.env` file.
    """

    # Security
    secret_key: str = "change-me"

    # Database (default to SQLite for local dev/tests; override in prod via env)
    database_url: str = "sqlite+aiosqlite:///./app.db"

    # Redis
    redis_url: AnyUrl = "redis://localhost:6379/0"

    # Misc
    api_v1_str: str = "/api/v1"
    project_name: str = "Wealth App API"
    allowed_origins: list[str] = []
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate settings once on import
settings = Settings()
