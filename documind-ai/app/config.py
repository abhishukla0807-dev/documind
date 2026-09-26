from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Identity
    APP_NAME: str = "DocuMind-AI"
    APP_ENV: str = "development"
    PORT: int = 8001
    HOST: str = "0.0.0.0"

    # Ollama Service
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "qwen2.5-coder:7b"

    # Qdrant Database
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Cloned Repositories Storage Root
    BASE_REPO_PATH: str = r"A:\documind\data\repos"

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached singleton instance of Settings.
    Ensures .env is read and validated once.
    """
    return Settings()