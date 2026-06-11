"""Notification provider implementations for multiple channels."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.models.enums import NotificationChannel


@dataclass(frozen=True)
class DeliveryResult:
    """Result of a notification delivery attempt."""

    provider_message_id: str | None
    accepted: bool
    error: str | None = None


class NotificationProvider(ABC):
    """Abstract base for all notification providers."""

    channel: NotificationChannel

    @abstractmethod
    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        """
        Send a notification through this provider.

        Args:
            recipient: Email, phone, or device ID depending on channel
            payload: Template-specific data (subject, body, title, etc.)

        Returns:
            DeliveryResult with status and provider message ID
        """
        raise NotImplementedError


class SmtpEmailProvider(NotificationProvider):
    """Email provider using SMTP."""

    channel = NotificationChannel.EMAIL

    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        """Send email via SMTP."""
        if not settings.smtp_enabled:
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error="SMTP provider not configured",
            )

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            subject = payload.get("subject", "OneTapGOV Notification")
            body_html = payload.get("body_html", "")
            body_text = payload.get("body_text", "")

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_from_email
            msg["To"] = recipient

            # Attach text and HTML parts
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            # Connect and send
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)

            await logger.ainfo(
                "email_sent",
                recipient=recipient,
                subject=subject,
            )

            return DeliveryResult(
                provider_message_id=f"smtp_{msg['Message-ID']}",
                accepted=True,
            )

        except Exception as exc:
            error_msg = str(exc)
            await logger.aerror("email_send_failed", recipient=recipient, error=error_msg)
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error=error_msg,
            )


class TwilioSmsProvider(NotificationProvider):
    """SMS provider using Twilio."""

    channel = NotificationChannel.SMS

    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        """Send SMS via Twilio."""
        if not settings.twilio_enabled:
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error="Twilio SMS provider not configured",
            )

        try:
            message_body = payload.get("body", "OneTapGOV: Check your scheme eligibility")

            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"

            auth = (settings.twilio_account_sid, settings.twilio_auth_token)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=auth,
                    data={
                        "From": settings.twilio_phone_number,
                        "To": recipient,
                        "Body": message_body,
                    },
                    timeout=10,
                )

            if response.status_code in (200, 201):
                result = response.json()
                message_id = result.get("sid")
                await logger.ainfo(
                    "sms_sent",
                    recipient=recipient,
                    message_id=message_id,
                )
                return DeliveryResult(
                    provider_message_id=message_id,
                    accepted=True,
                )
            else:
                error_msg = f"Twilio returned {response.status_code}: {response.text}"
                await logger.aerror("sms_send_failed", recipient=recipient, error=error_msg)
                return DeliveryResult(
                    provider_message_id=None,
                    accepted=False,
                    error=error_msg,
                )

        except Exception as exc:
            error_msg = str(exc)
            await logger.aerror("sms_send_failed", recipient=recipient, error=error_msg)
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error=error_msg,
            )


class TwilioWhatsappProvider(NotificationProvider):
    """WhatsApp provider using Twilio."""

    channel = NotificationChannel.WHATSAPP

    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        """Send WhatsApp message via Twilio."""
        if not settings.twilio_enabled:
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error="Twilio WhatsApp provider not configured",
            )

        try:
            message_body = payload.get("body", "OneTapGOV: Check your scheme eligibility")

            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"

            auth = (settings.twilio_account_sid, settings.twilio_auth_token)

            # WhatsApp phone numbers must have format +country_code_number
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=auth,
                    data={
                        "From": f"whatsapp:{settings.twilio_whatsapp_number}",
                        "To": f"whatsapp:{recipient}",
                        "Body": message_body,
                    },
                    timeout=10,
                )

            if response.status_code in (200, 201):
                result = response.json()
                message_id = result.get("sid")
                await logger.ainfo(
                    "whatsapp_sent",
                    recipient=recipient,
                    message_id=message_id,
                )
                return DeliveryResult(
                    provider_message_id=message_id,
                    accepted=True,
                )
            else:
                error_msg = f"Twilio WhatsApp returned {response.status_code}: {response.text}"
                await logger.aerror(
                    "whatsapp_send_failed",
                    recipient=recipient,
                    error=error_msg,
                )
                return DeliveryResult(
                    provider_message_id=None,
                    accepted=False,
                    error=error_msg,
                )

        except Exception as exc:
            error_msg = str(exc)
            await logger.aerror("whatsapp_send_failed", recipient=recipient, error=error_msg)
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error=error_msg,
            )


class FirebasePushProvider(NotificationProvider):
    """Push notification provider using Firebase Cloud Messaging."""

    channel = NotificationChannel.PUSH

    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        """Send push notification via Firebase."""
        if not settings.firebase_enabled:
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error="Firebase provider not configured",
            )

        try:
            # recipient should be the Firebase device token
            title = payload.get("title", "OneTapGOV")
            body = payload.get("body", "Check your scheme eligibility")
            data = payload.get("data", {})

            url = "https://fcm.googleapis.com/v1/projects/{}/messages:send".format(
                settings.firebase_project_id
            )

            headers = {
                "Authorization": f"Bearer {settings.firebase_access_token}",
                "Content-Type": "application/json",
            }

            message_payload = {
                "message": {
                    "token": recipient,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": data,
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=message_payload,
                    timeout=10,
                )

            if response.status_code in (200, 201):
                result = response.json()
                message_id = result.get("name", "").split("/")[-1]
                await logger.ainfo(
                    "push_sent",
                    recipient=recipient,
                    message_id=message_id,
                )
                return DeliveryResult(
                    provider_message_id=message_id,
                    accepted=True,
                )
            else:
                error_msg = f"Firebase returned {response.status_code}: {response.text}"
                await logger.aerror("push_send_failed", recipient=recipient, error=error_msg)
                return DeliveryResult(
                    provider_message_id=None,
                    accepted=False,
                    error=error_msg,
                )

        except Exception as exc:
            error_msg = str(exc)
            await logger.aerror("push_send_failed", recipient=recipient, error=error_msg)
            return DeliveryResult(
                provider_message_id=None,
                accepted=False,
                error=error_msg,
            )


class UnconfiguredProvider(NotificationProvider):
    """Fallback provider when no real provider is configured."""

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel

    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        return DeliveryResult(
            provider_message_id=None,
            accepted=False,
            error=f"No {self.channel} provider is configured",
        )
