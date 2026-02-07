from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4.1"

    # Postgres
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/phishing_detect"
    db_echo: bool = False


settings = Settings()
