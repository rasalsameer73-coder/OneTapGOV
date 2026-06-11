from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "OneTapGOV API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="development-only-secret-key-change-me", min_length=32)
    access_token_ttl_minutes: int = Field(default=15, ge=5, le=60)
    refresh_token_ttl_days: int = Field(default=30, ge=1, le=90)

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/onetapgov"
    database_pool_size: int = Field(default=20, ge=5, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=100)
    database_pool_timeout_seconds: int = Field(default=30, ge=5, le=120)

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    cors_origins: list[str] = ["http://localhost:5173"]
    trusted_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    rate_limit_requests: int = Field(default=120, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    ai_rate_limit_requests: int = Field(default=20, ge=1)

    ai_provider: str = "stub"
    ai_model: str = "structured-extractor-v1"
    ai_cost_per_1k_input_tokens: float = Field(default=0, ge=0)
    ai_cost_per_1k_output_tokens: float = Field(default=0, ge=0)

    supabase_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_jwt_audience: str = "authenticated"
    supabase_jwt_issuer: str | None = None

    log_level: str = "INFO"
    enable_docs: bool = True

    # Email (SMTP) Provider
    smtp_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "noreply@onetapgov.in"

    # SMS Provider (Twilio)
    twilio_enabled: bool = False
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    twilio_whatsapp_number: str | None = None

    # Push Notification Provider (Firebase)
    firebase_enabled: bool = False
    firebase_project_id: str | None = None
    firebase_access_token: str | None = None

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("secret_key")
    @classmethod
    def reject_default_secret_in_production(cls, value: str, info) -> str:
        environment = info.data.get("environment", "development")
        if environment == "production" and value.startswith("development-only"):
            raise ValueError("SECRET_KEY must be changed in production")
        return value

    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.enable_docs else None

    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.enable_docs else None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
