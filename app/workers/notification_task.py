from typing import Dict

from app.workers.celery_app import celery


def send_notification_impl(provider: str, recipient: str, payload: Dict) -> Dict:
    """Lightweight, testable implementation for sending a notification.
    """
    return {"provider": provider, "recipient": recipient, "status": "sent", "payload": payload}


send_notification = celery.task(name="workers.send_notification")(send_notification_impl)
