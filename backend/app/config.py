import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "LCA Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_SECRET_KEY: str = "change-me-to-a-random-secret-key-in-production"
    APP_ALGORITHM: str = "HS256"
    APP_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str = "sqlite:///./lca_platform.db"
    DATABASE_ECHO: bool = False

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODEL_DIR: str = str(BASE_DIR / "backend" / "models")
    OUTPUT_DIR: str = str(BASE_DIR / "backend" / "outputs")
    DATA_DIR: str = str(BASE_DIR / "backend" / "data")

    ORIGINAL_DATA_DIR: str = str(BASE_DIR.parent)

    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
