import asyncio
from typing import Dict

from app.core.cache import cache
from app.workers.celery_app import celery
from app.core.logging import logger


def _clear_recommendations_cache() -> Dict:
    try:
        asyncio.run(cache.delete_pattern("recommendations:*"))
        return {"status": "ok", "cleared": True}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def refresh_recommendations_impl() -> Dict:
    result = _clear_recommendations_cache()
    if result.get("status") == "ok":
        logger.info("maintenance.refresh_recommendations", result=result)
    else:
        logger.error("maintenance.refresh_recommendations_failed", result=result)
    return result


refresh_recommendations = celery.task(name="workers.refresh_recommendations")(refresh_recommendations_impl)
