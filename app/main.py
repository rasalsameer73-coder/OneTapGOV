from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.cache import cache
from app.core.config import settings
from app.core.database import close_database
from app.core.exceptions import AppError
from app.core.logging import configure_logging, logger
from app.middleware.rate_limit import RedisRateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.trace import TraceMiddleware
from app.middleware.principal import PrincipalMiddleware

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await logger.ainfo("application_starting", environment=settings.environment)
    yield
    await cache.close()
    await close_database()
    await logger.ainfo("application_stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "OneTapGOV backend. AI extracts facts; versioned rules decide eligibility; "
        "the database records and verifies decisions."
    ),
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(RedisRateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TraceMiddleware)
app.add_middleware(PrincipalMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "unavailable")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": exc.errors
            or [{"code": exc.code, "field": None, "detail": exc.message}],
            "trace_id": _trace_id(request),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "code": "validation_error",
            "field": ".".join(str(part) for part in item["loc"] if part != "body"),
            "detail": item["msg"],
        }
        for item in exc.errors()
    ]
    return ORJSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Request validation failed",
            "data": None,
            "errors": errors,
            "trace_id": _trace_id(request),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None,
            "errors": [
                {"code": "http_error", "field": None, "detail": str(exc.detail)}
            ],
            "trace_id": _trace_id(request),
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    await logger.aexception("unhandled_exception", error=str(exc))
    return ORJSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal error occurred",
            "data": None,
            "errors": [
                {
                    "code": "internal_error",
                    "field": None,
                    "detail": "Contact support with the trace ID",
                }
            ],
            "trace_id": _trace_id(request),
        },
    )


@app.get("/health", tags=["Operations"])
async def health(request: Request):
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {"status": "ok", "version": settings.app_version},
        "errors": [],
        "trace_id": _trace_id(request),
    }

