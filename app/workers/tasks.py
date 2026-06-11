import asyncio
from uuid import UUID

from app.core.database import AsyncSessionFactory
from app.models.operations import Notification
from app.services.notifications import NotificationService
from app.services.recommendations import RecommendationService
from app.workers.celery_app import celery_app


@celery_app.task(
    name="recommendations.generate",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def generate_recommendations(user_id: str) -> list[dict]:
    async def run() -> list[dict]:
        async with AsyncSessionFactory() as session:
            return await RecommendationService(session).generate(UUID(user_id))

    return asyncio.run(run())


@celery_app.task(
    name="notifications.dispatch",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def dispatch_notification(notification_id: str) -> dict:
    async def run() -> dict:
        async with AsyncSessionFactory() as session:
            notification = await session.get(Notification, UUID(notification_id))
            if notification is None:
                return {"status": "not_found", "notification_id": notification_id}
            result = await NotificationService(session).dispatch(notification)
            return {"status": str(result.status), "notification_id": notification_id}

    return asyncio.run(run())

