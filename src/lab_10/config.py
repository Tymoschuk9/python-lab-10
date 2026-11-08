from __future__ import annotations

import os
from functools import lru_cache

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        app_name: str = "Online Store Manager"
        environment: str = "development"
        database_url: str = "sqlite:///shop.db"
        log_level: str = "INFO"

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )
except ImportError:
    class Settings:
        def __init__(self) -> None:
            self.app_name = os.getenv("APP_NAME", "Online Store Manager")
            self.environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development"))
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///shop.db")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
