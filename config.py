"""
Centralized application configuration.
Loads values from environment variables / .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = "sk-placeholder"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/incident_copilot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Vector store
    vector_db_path: str = "./embeddings/faiss_index"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we don't re-read env vars on every call."""
    return Settings()
