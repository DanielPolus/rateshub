# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = Field(..., description="SQLAlchemy DSN, e.g. postgresql+psycopg2://user:pass@host:5432/db")
    REDIS_URL: str = "redis://localhost:6379/0"
    API_SOURCE: str = "frankfurter"
    ETL_BACKFILL_START: str = "2015-01-01"
    APP_NAME: str = "RatesHub"

settings = Settings()
