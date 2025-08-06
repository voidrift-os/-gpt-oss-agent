from pydantic_settings import BaseSettings
from pydantic import AnyUrl, PostgresDsn

class Settings(BaseSettings):
    # Security
    secret_key: str
    # Database
    database_url: PostgresDsn
    # Redis
    redis_url: AnyUrl
    # Misc
    api_v1_str: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()