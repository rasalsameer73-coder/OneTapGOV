import time
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.trace_id = trace_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            await logger.aexception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            raise
        response.headers["X-Request-ID"] = trace_id
        await logger.ainfo(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return response

