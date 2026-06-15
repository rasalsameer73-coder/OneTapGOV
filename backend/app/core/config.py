from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    PROJECT_NAME: str = "OneTapGOV"

    API_V1_PREFIX: str = "/api/v1"

    DEBUG: bool = True

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = ""

    REDIS_URL: str = ""

    SUPABASE_URL: str = ""

    SUPABASE_KEY: str = ""

    SUPABASE_JWT_SECRET: str = ""

    OPENAI_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

    SECRET_KEY: str = ""

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    UPLOAD_DIRECTORY: str = "uploads"

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


try:
    settings = Settings()
except Exception:
    # Fall back to loading from the project's .env to avoid import-time
    # failures when the host environment supplies invalid values.
    import traceback
    traceback.print_exc()
    # Temporarily remove problematic env vars (like DEBUG) so the .env file
    # values are used when creating Settings.
    import os

    orig_debug = os.environ.pop("DEBUG", None)
    try:
        settings = Settings(_env_file=".env")
    finally:
        if orig_debug is not None:
            os.environ["DEBUG"] = orig_debug