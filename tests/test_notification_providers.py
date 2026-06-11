"""Tests for notification providers."""

import pytest

from app.models.enums import NotificationChannel
from app.services.notification_providers import (
    FirebasePushProvider,
    SmtpEmailProvider,
    TwilioSmsProvider,
    TwilioWhatsappProvider,
    UnconfiguredProvider,
)


@pytest.mark.asyncio
class TestSmtpEmailProvider:
    async def test_send_without_smtp_configured(self, monkeypatch):
        """Test email provider when SMTP is not configured."""
        monkeypatch.setattr("app.services.notification_providers.settings.smtp_enabled", False)
        provider = SmtpEmailProvider()
        result = await provider.send(
            "user@example.com",
            {"subject": "Test", "body_html": "<p>Test</p>"},
        )
        assert result.accepted is False
        assert "not configured" in (result.error or "").lower()

    async def test_provider_channel(self):
        """Test that provider has correct channel."""
        provider = SmtpEmailProvider()
        assert provider.channel == NotificationChannel.EMAIL


@pytest.mark.asyncio
class TestTwilioSmsProvider:
    async def test_send_without_twilio_configured(self, monkeypatch):
        """Test SMS provider when Twilio is not configured."""
        monkeypatch.setattr("app.services.notification_providers.settings.twilio_enabled", False)
        provider = TwilioSmsProvider()
        result = await provider.send(
            "+1234567890",
            {"body": "Test message"},
        )
        assert result.accepted is False
        assert "not configured" in (result.error or "").lower()

    async def test_provider_channel(self):
        """Test that provider has correct channel."""
        provider = TwilioSmsProvider()
        assert provider.channel == NotificationChannel.SMS


@pytest.mark.asyncio
class TestTwilioWhatsappProvider:
    async def test_send_without_twilio_configured(self, monkeypatch):
        """Test WhatsApp provider when Twilio is not configured."""
        monkeypatch.setattr("app.services.notification_providers.settings.twilio_enabled", False)
        provider = TwilioWhatsappProvider()
        result = await provider.send(
            "+1234567890",
            {"body": "Test message"},
        )
        assert result.accepted is False
        assert "not configured" in (result.error or "").lower()

    async def test_provider_channel(self):
        """Test that provider has correct channel."""
        provider = TwilioWhatsappProvider()
        assert provider.channel == NotificationChannel.WHATSAPP


@pytest.mark.asyncio
class TestFirebasePushProvider:
    async def test_send_without_firebase_configured(self, monkeypatch):
        """Test push provider when Firebase is not configured."""
        monkeypatch.setattr("app.services.notification_providers.settings.firebase_enabled", False)
        provider = FirebasePushProvider()
        result = await provider.send(
            "device_token_123",
            {"title": "Test", "body": "Test message"},
        )
        assert result.accepted is False
        assert "not configured" in (result.error or "").lower()

    async def test_provider_channel(self):
        """Test that provider has correct channel."""
        provider = FirebasePushProvider()
        assert provider.channel == NotificationChannel.PUSH


@pytest.mark.asyncio
class TestUnconfiguredProvider:
    async def test_send_returns_error(self):
        """Test that unconfigured provider always fails."""
        provider = UnconfiguredProvider(NotificationChannel.EMAIL)
        result = await provider.send(
            "user@example.com",
            {"subject": "Test"},
        )
        assert result.accepted is False
        assert "configured" in (result.error or "").lower()
        assert result.provider_message_id is None

    async def test_all_channels(self):
        """Test unconfigured provider for all channels."""
        for channel in NotificationChannel:
            provider = UnconfiguredProvider(channel)
            assert provider.channel == channel
            result = await provider.send("recipient", {})
            assert result.accepted is False
