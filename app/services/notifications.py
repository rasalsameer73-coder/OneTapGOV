from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import NotificationChannel, NotificationStatus
from app.models.operations import Notification
from app.repositories.operations import OperationsRepository
from app.services.notification_providers import (
    DeliveryResult,
    FirebasePushProvider,
    SmtpEmailProvider,
    TwilioSmsProvider,
    TwilioWhatsappProvider,
    UnconfiguredProvider,
)


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.operations = OperationsRepository(session)
        self.providers = self._initialize_providers()

    @staticmethod
    def _initialize_providers() -> dict[NotificationChannel, object]:
        """Initialize providers based on configuration."""
        providers = {}

        # Email provider
        if settings.smtp_enabled:
            providers[NotificationChannel.EMAIL] = SmtpEmailProvider()
        else:
            providers[NotificationChannel.EMAIL] = UnconfiguredProvider(NotificationChannel.EMAIL)

        # SMS provider
        if settings.twilio_enabled:
            providers[NotificationChannel.SMS] = TwilioSmsProvider()
        else:
            providers[NotificationChannel.SMS] = UnconfiguredProvider(NotificationChannel.SMS)

        # WhatsApp provider
        if settings.twilio_enabled:
            providers[NotificationChannel.WHATSAPP] = TwilioWhatsappProvider()
        else:
            providers[NotificationChannel.WHATSAPP] = UnconfiguredProvider(
                NotificationChannel.WHATSAPP
            )

        # Push notification provider
        if settings.firebase_enabled:
            providers[NotificationChannel.PUSH] = FirebasePushProvider()
        else:
            providers[NotificationChannel.PUSH] = UnconfiguredProvider(NotificationChannel.PUSH)

        return providers

    async def queue(
        self,
        *,
        user_id: UUID,
        channel: NotificationChannel,
        recipient: str,
        template_code: str,
        payload: dict,
    ) -> Notification:
        entity = await self.operations.add(
            Notification(
                user_id=user_id,
                channel=channel,
                recipient=recipient,
                template_code=template_code,
                payload=payload,
                status=NotificationStatus.QUEUED,
            )
        )
        await self.session.commit()
        return entity

    async def dispatch(self, notification: Notification) -> Notification:
        result = await self.providers[NotificationChannel(notification.channel)].send(
            notification.recipient, notification.payload
        )
        notification.status = (
            NotificationStatus.SENT if result.accepted else NotificationStatus.FAILED
        )
        notification.provider_message_id = result.provider_message_id
        notification.error_message = result.error
        notification.sent_at = datetime.now(UTC) if result.accepted else None
        await self.session.commit()
        return notification

    async def list(self, user_id: UUID) -> list[Notification]:
        return await self.operations.list_notifications(user_id)
