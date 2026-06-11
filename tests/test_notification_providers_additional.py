import asyncio
from types import SimpleNamespace

import pytest

import httpx

from app.services.notification_providers import (
    DeliveryResult,
    SmtpEmailProvider,
    TwilioSmsProvider,
    TwilioWhatsappProvider,
    FirebasePushProvider,
    UnconfiguredProvider,
)
from app.models.enums import NotificationChannel
from app.core.config import settings


@pytest.mark.asyncio
async def test_unconfigured_provider_returns_false():
    p = UnconfiguredProvider(NotificationChannel.EMAIL)
    res = await p.send("to", {"message": "x"})
    assert isinstance(res, DeliveryResult)
    assert res.accepted is False


@pytest.mark.asyncio
async def test_smtp_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "smtp_enabled", False)
    p = SmtpEmailProvider()
    res = await p.send("user@example.com", {"body_text": "hi"})
    assert res.accepted is False


@pytest.mark.asyncio
async def test_smtp_success(monkeypatch):
    monkeypatch.setattr(settings, "smtp_enabled", True)
    monkeypatch.setattr(settings, "smtp_from_email", "noreply@example.com")

    class FakeSMTP:
        def __init__(self, *a, **k):
            pass

        def starttls(self):
            pass

        def login(self, u, p):
            pass

        def send_message(self, msg):
            # ensure Message-ID exists for provider_message_id
            msg["Message-ID"] = "<msg-1>"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)

    p = SmtpEmailProvider()
    res = await p.send("user@example.com", {"body_text": "hi"})
    assert res.accepted is True
    assert res.provider_message_id.startswith("smtp_")


@pytest.mark.asyncio
async def test_twilio_sms_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "twilio_enabled", False)
    p = TwilioSmsProvider()
    res = await p.send("+1000000000", {"body": "x"})
    assert res.accepted is False


@pytest.mark.asyncio
async def test_twilio_sms_success(monkeypatch):
    monkeypatch.setattr(settings, "twilio_enabled", True)

    class DummyResponse:
        def __init__(self, code, body):
            self.status_code = code
            self._body = body

        def json(self):
            return self._body

        @property
        def text(self):
            return str(self._body)

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *a, **k):
            return DummyResponse(201, {"sid": "sid-1"})

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    p = TwilioSmsProvider()
    res = await p.send("+1000000000", {"body": "x"})
    assert res.accepted is True
    assert res.provider_message_id == "sid-1"


@pytest.mark.asyncio
async def test_twilio_whatsapp_success(monkeypatch):
    monkeypatch.setattr(settings, "twilio_enabled", True)

    class DummyResponse:
        def __init__(self, code, body):
            self.status_code = code
            self._body = body

        def json(self):
            return self._body

        @property
        def text(self):
            return str(self._body)

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *a, **k):
            return DummyResponse(201, {"sid": "wh-sid"})

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    p = TwilioWhatsappProvider()
    res = await p.send("+1000000000", {"body": "x"})
    assert res.accepted is True
    assert res.provider_message_id == "wh-sid"


@pytest.mark.asyncio
async def test_firebase_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "firebase_enabled", False)
    p = FirebasePushProvider()
    res = await p.send("token", {"body": "x"})
    assert res.accepted is False


@pytest.mark.asyncio
async def test_firebase_success(monkeypatch):
    monkeypatch.setattr(settings, "firebase_enabled", True)
    monkeypatch.setattr(settings, "firebase_project_id", "proj-1")
    monkeypatch.setattr(settings, "firebase_access_token", "token")

    class DummyResponse:
        def __init__(self, code, body):
            self.status_code = code
            self._body = body

        def json(self):
            return self._body

        @property
        def text(self):
            return str(self._body)

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *a, **k):
            return DummyResponse(200, {"name": "projects/proj-1/messages/msg-1"})

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    p = FirebasePushProvider()
    res = await p.send("token", {"body": "x"})
    assert res.accepted is True
    assert res.provider_message_id == "msg-1"
