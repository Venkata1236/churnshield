from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
SAVED_MODELS_DIR = BASE_DIR / "saved_models"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "ChurnShield API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    api_prefix: str = "/api/v1"

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # Database
    database_url: str = Field(default="", alias="DATABASE_URL")

    # ML
    model_path: str = Field(
        default=str(SAVED_MODELS_DIR / "churn_model.pkl"),
        alias="MODEL_PATH",
    )
    feature_names_path: str = Field(
        default=str(SAVED_MODELS_DIR / "feature_names.json"),
        alias="FEATURE_NAMES_PATH",
    )

    # LangSmith
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="churnshield", alias="LANGCHAIN_PROJECT")

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://churnshield.vercel.app",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()