from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import logger


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.redis = None
        self.redis_unavailable = False
        self._redis_warning_logged = False

    async def _get_redis(self):
        """Lazily initialize Redis connection."""
        if self.redis is not None:
            return self.redis
        if self.redis_unavailable:
            return None
        try:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
            return self.redis
        except Exception as exc:
            self.redis_unavailable = True
            if not self._redis_warning_logged:
                await logger.awarning(
                    "rate_limit_backend_unavailable",
                    error=str(exc),
                    detail="Rate limiting disabled. Restart with Redis for production.",
                )
                self._redis_warning_logged = True
            return None

    async def dispatch(self, request, call_next):
        if settings.environment == "test":
            return await call_next(request)
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)

        redis = await self._get_redis()
        if redis is None:
            # Redis unavailable - skip rate limiting, allow request through
            return await call_next(request)

        limit = (
            settings.ai_rate_limit_requests
            if request.url.path.endswith("/ai/extract")
            else settings.rate_limit_requests
        )
        identifier = request.client.host if request.client else "unknown"
        key = f"ratelimit:{request.url.path}:{identifier}"
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, settings.rate_limit_window_seconds)
            if count > limit:
                trace_id = getattr(request.state, "trace_id", "unavailable")
                return ORJSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded",
                        "data": None,
                        "errors": [
                            {
                                "code": "rate_limit_exceeded",
                                "field": None,
                                "detail": "Try again after the rate-limit window",
                            }
                        ],
                        "trace_id": trace_id,
                    },
                    headers={"Retry-After": str(settings.rate_limit_window_seconds)},
                )
        except Exception as exc:
            await logger.awarning("rate_limit_check_failed", error=str(exc))
        return await call_next(request)
