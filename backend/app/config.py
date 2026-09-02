"""Application configuration using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (02-AI_Organaizer/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Database directory and file
# In Docker: /app/data/ai_organizer.db (mounted volume)
# Locally: backend/data/ai_organizer.db
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "ai_organizer.db"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    api_base_url: str = "http://localhost:18080"
    database_url: str = f"sqlite:///{DB_FILE}"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
