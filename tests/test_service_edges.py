from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.enums import NotificationChannel, NotificationStatus
from app.services.notifications import (
    DeliveryResult,
    NotificationService,
    UnconfiguredProvider,
)
from app.services.profiles import ProfileService
from app.utils.sanitization import normalize_email, sanitize_text


def test_sanitization_and_profile_age():
    assert sanitize_text("  Citizen\x00 Name  ") == "Citizen Name"
    assert normalize_email(" User@Example.COM ") == "user@example.com"
    assert ProfileService._age(__import__("datetime").date(2000, 1, 1)) >= 26


@pytest.mark.asyncio
async def test_unconfigured_notification_provider_and_dispatch(session):
    provider = UnconfiguredProvider(NotificationChannel.SMS)
    result = await provider.send("+910000000000", {"message": "test"})
    assert result.accepted is False
    assert "configured" in result.error

    service = NotificationService(session)
    notification = SimpleNamespace(
        channel=NotificationChannel.EMAIL,
        recipient="citizen@example.com",
        payload={"message": "hello"},
        status=NotificationStatus.QUEUED,
        provider_message_id=None,
        error_message=None,
        sent_at=None,
    )
    dispatched = await service.dispatch(notification)
    assert dispatched.status == NotificationStatus.FAILED
    assert dispatched.error_message


@pytest.mark.asyncio
async def test_successful_notification_dispatch(session):
    class Provider:
        async def send(self, recipient, payload):
            return DeliveryResult(provider_message_id="provider-1", accepted=True)

    service = NotificationService(session)
    service.providers[NotificationChannel.PUSH] = Provider()
    notification = SimpleNamespace(
        channel=NotificationChannel.PUSH,
        recipient="device-token",
        payload={"message": "ready"},
        status=NotificationStatus.QUEUED,
        provider_message_id=None,
        error_message=None,
        sent_at=None,
    )
    dispatched = await service.dispatch(notification)
    assert dispatched.status == NotificationStatus.SENT
    assert dispatched.provider_message_id == "provider-1"
    assert dispatched.sent_at is not None
