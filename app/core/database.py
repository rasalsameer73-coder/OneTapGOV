from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def create_database_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or settings.database_url
    common = {
        "pool_pre_ping": True,
        "echo": False,
    }
    if url.startswith("sqlite"):
        return create_async_engine(url, **common)
    return create_async_engine(
        url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout_seconds,
        pool_recycle=1800,
        connect_args={"server_settings": {"application_name": "onetapgov-api"}},
        **common,
    )


engine = create_database_engine()
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def close_database() -> None:
    await engine.dispose()

