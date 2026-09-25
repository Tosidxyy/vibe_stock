"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StockPilot"
    environment: str = "development"
    model_name: str = ""
    model_api_key: str = ""
    model_base_url: str = ""
    database_url: str = "sqlite:///./stockpilot.db"
    market_data_provider: str = "eastmoney"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
