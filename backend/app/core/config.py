import os
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
SAVED_MODELS_DIR = BASE_DIR / "saved_models"


class Settings(BaseSettings):
    APP_NAME: str = "ChurnShield API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    OPENAI_API_KEY: str = ""
    DATABASE_URL: Optional[str] = None

    MODEL_PATH: str = str(SAVED_MODELS_DIR / "churn_model.pkl")
    FEATURE_NAMES_PATH: str = str(SAVED_MODELS_DIR / "feature_names.json")

    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_PROJECT: str = "churnshield"

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

if not settings.DATABASE_URL:
    logger.warning("No DATABASE_URL — running DB-less mode (local dev)")