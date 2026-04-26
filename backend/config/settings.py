from pathlib import Path
from pydantic_settings import BaseSettings

# The .env file lives at the project root (one level above 'backend/')
_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_URL: str = "http://localhost:6333"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:dev@localhost/finance_db"

    model_config = {
        "env_file": str(_ROOT / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
