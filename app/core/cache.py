import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import logger


class Cache:
    def __init__(self, redis_url: str = settings.redis_url) -> None:
        self.client = Redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )

    async def get_json(self, key: str) -> Any | None:
        if settings.environment == "test":
            return None
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as exc:
            await logger.awarning("cache_read_failed", key=key, error=str(exc))
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if settings.environment == "test":
            return
        try:
            await self.client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
        except Exception as exc:
            await logger.awarning("cache_write_failed", key=key, error=str(exc))

    async def delete_pattern(self, pattern: str) -> None:
        if settings.environment == "test":
            return
        try:
            async for key in self.client.scan_iter(match=pattern, count=100):
                await self.client.delete(key)
        except Exception as exc:
            await logger.awarning("cache_invalidation_failed", pattern=pattern, error=str(exc))

    async def close(self) -> None:
        await self.client.aclose()


cache = Cache()


async def get_json(key: str):
    """Module-level helper for tests and convenience."""
    return await cache.get_json(key)


async def set_json(key: str, value: Any, ttl_seconds: int = 300):
    return await cache.set_json(key, value, ttl_seconds)
