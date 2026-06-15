from pathlib import Path
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from fastapi import HTTPException
from starlette import status
import traceback


# Database Engine
engine = None


def _create_engine(url: str):
    try:
        return create_async_engine(
            url,
            echo=settings.DEBUG,

            # IMPORTANT for Supabase
            pool_pre_ping=True,
            pool_recycle=300,

            # optional
            pool_size=5,
            max_overflow=10,
        )

    except Exception:
        traceback.print_exc()
        return None


# Primary database
if settings.DATABASE_URL:
    engine = _create_engine(settings.DATABASE_URL)


# Development fallback
if engine is None and settings.ENVIRONMENT == "development":
    try:
        dev_db_path = Path(".") / "dev.db"

        sqlite_url = (
            f"sqlite+aiosqlite:///{dev_db_path.as_posix()}"
        )

        engine = _create_engine(sqlite_url)

        if engine is not None:
            print(f"Using SQLite dev DB at {dev_db_path}")

    except Exception:
        traceback.print_exc()


# Session Factory
AsyncSessionLocal = None

if engine is not None:
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# Base Model
class Base(DeclarativeBase):
    pass


# Dependency
async def get_db():

    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Database is not configured or failed "
                "to initialize."
            ),
        )

    async with AsyncSessionLocal() as session:
        yield session