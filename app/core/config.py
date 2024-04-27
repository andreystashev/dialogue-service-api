import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, validator


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    COUNT_REQUESTS_PER_MINUTES: int

    # FastAPI
    BACKEND_DOMAIN: str = os.getenv("BACKEND_DOMAIN", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Botan Task"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14  # 2 weeks
    ACCESS_TOKEN_REFRESH_MINUTES = 60 * 24 * 28  # 4 weeks
    COUNT_REQUEST_DIALOG_PER_MINUTES = 3
    BACKEND_CORS_ORIGINS = ["*"]

    # openai
    OPENAI_URL: str
    OPENAI_TOKEN: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    QUEUE_NAME: str = "default"

    # Database
    POSTGRES_HOSTNAME: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOSTNAME"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"


settings = Settings()
