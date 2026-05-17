from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = Field(default="Weather Query App", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    openweather_api_key: str = Field(default="", alias="OPENWEATHER_API_KEY")
    openweather_base_url: str = Field(default="https://api.openweathermap.org/data/2.5", alias="OPENWEATHER_BASE_URL")
    rate_limit_per_minute: int = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    page_size_default: int = Field(default=10, alias="PAGE_SIZE_DEFAULT")
    external_api_timeout_seconds: float = Field(default=10.0, alias="EXTERNAL_API_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()