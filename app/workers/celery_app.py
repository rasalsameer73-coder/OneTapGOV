from celery import Celery

from app.core.config import settings


# Build broker URL from settings (falls back to REDIS env vars)
broker = getattr(settings, "celery_broker_url", None)
if not broker:
    redis_host = getattr(settings, "redis_host", "localhost")
    redis_port = getattr(settings, "redis_port", 6379)
    broker = f"redis://{redis_host}:{redis_port}/0"


celery = Celery("one_tap_gov", broker=broker)
celery.conf.update(
    result_backend=broker,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    enable_utc=True,
    timezone="UTC",
)

# Periodic tasks (beat) schedule: refresh recommendations cache every 10 minutes
celery.conf.beat_schedule = {
    "refresh-recommendations-cache": {
        "task": "workers.refresh_recommendations",
        "schedule": 600.0,
    }
}

# Daily recompute of recommendations (run at 03:00 UTC)
celery.conf.beat_schedule["recompute-recommendations-daily"] = {
    "task": "workers.recompute_recommendations",
    "schedule": 24 * 3600.0,
}
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "onetapgov",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
)

