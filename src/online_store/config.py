from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field, AliasChoices

    class Settings(BaseSettings):
        app_name: str = Field(default="Online Store Manager", validation_alias=AliasChoices("APP_NAME", "app_name"))
        app_env: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "app_env", "ENVIRONMENT", "environment"))
        environment: str = Field(default="development", validation_alias=AliasChoices("ENVIRONMENT", "environment", "APP_ENV", "app_env"))
        database_url: str = Field(default="sqlite:///shop.db", validation_alias=AliasChoices("DATABASE_URL", "database_url"))
        log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level"))

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )
except (ImportError, Exception):
    class Settings:
        def __init__(self) -> None:
            self.app_name = os.getenv("APP_NAME", "Online Store Manager")
            self.app_env = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development"))
            self.environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development"))
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///shop.db")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
