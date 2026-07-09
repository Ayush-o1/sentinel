"""
SENTINEL — Application Configuration

Uses Pydantic Settings to load configuration from environment variables.
All settings are type-safe and validated at startup.

Pattern:
    Settings are accessed via the module-level `settings` singleton.
    Never import os.environ directly in application code — always use `settings`.
"""

from functools import lru_cache
from typing import List

from pydantic import PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All fields have sensible defaults for local development.
    Production deployments MUST override SECRET_KEY and DB credentials.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Silently ignore unknown env vars
    )

    # ---- Application ----
    APP_ENV: str = "development"
    APP_NAME: str = "SENTINEL"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ---- Server ----
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ---- Security ----
    SECRET_KEY: str  # Required — no default (fail fast if missing)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- Database ----
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sentinel"
    POSTGRES_USER: str = "sentinel_user"
    POSTGRES_PASSWORD: str  # Required — no default

    # Assembled connection URL (built from the components above)
    # asyncpg dialect for async SQLAlchemy
    DATABASE_URL: str = ""

    # ---- CORS ----
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ---- Production Security ----
    ALLOWED_HOSTS: List[str] = ["*"]

    # ---- Rate Limiting ----
    RATE_LIMIT_PREDICT: str = "30/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_REGISTER: str = "5/minute"

    # ---- ML Model ----
    ACTIVE_MODEL_VERSION: str = "1.0.0"
    MODEL_FILE_NAME: str = "sentinel_v1.0.0.joblib"

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}, got '{v}'")
        return v

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """
        Construct the async PostgreSQL connection URL from individual components.
        This prevents accidental misconfiguration from mixing connection parts.
        """
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
                f"/{self.POSTGRES_DB}"
            )
        return self

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    The @lru_cache decorator ensures the .env file is read exactly once
    during the application lifecycle, not on every request.
    """
    return Settings()


# Module-level singleton — the canonical way to access settings
settings: Settings = get_settings()
