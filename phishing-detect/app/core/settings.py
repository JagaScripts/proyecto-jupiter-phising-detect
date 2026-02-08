from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Carga y valida la configuración de la app desde variables de entorno.
    Define defaults y un punto único de acceso a los settings.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4.1"

    # Postgres
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/phishing_detect"
    db_echo: bool = False


settings = Settings()
