from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from jose import jwt

import app.core.security as security
import app.services.auth as auth_module
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_supabase_token
from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_legacy_supabase_token_verification(monkeypatch):
    secret = "supabase-test-secret-with-at-least-thirty-two-characters"
    issuer = "https://project.supabase.co/auth/v1"
    monkeypatch.setattr(settings, "supabase_url", "https://project.supabase.co")
    monkeypatch.setattr(settings, "supabase_jwt_secret", secret)
    monkeypatch.setattr(settings, "supabase_publishable_key", None)
    monkeypatch.setattr(settings, "supabase_jwt_issuer", issuer)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "email": "supabase@example.com",
            "aud": "authenticated",
            "iss": issuer,
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )
    payload = await decode_supabase_token(token)
    assert payload["email"] == "supabase@example.com"
    with pytest.raises(ValueError):
        await decode_supabase_token("not-a-jwt")


@pytest.mark.asyncio
async def test_supabase_exchange_creates_and_reuses_identity(session, monkeypatch):
    supabase_id = uuid4()

    async def valid_token(_):
        return {
            "sub": str(supabase_id),
            "email": "linked@example.com",
            "email_confirmed_at": "2026-01-01T00:00:00Z",
            "user_metadata": {"name": "Linked User"},
        }

    monkeypatch.setattr(auth_module, "decode_supabase_token", valid_token)
    service = AuthService(session)
    user, tokens = await service.exchange_supabase_token(
        "token", user_agent="pytest", ip_address="127.0.0.1"
    )
    assert user.supabase_user_id == supabase_id
    assert user.is_verified is True
    assert tokens.access_token

    same_user, _ = await service.exchange_supabase_token(
        "token", user_agent=None, ip_address=None
    )
    assert same_user.id == user.id

    async def invalid_token(_):
        raise ValueError("invalid")

    monkeypatch.setattr(auth_module, "decode_supabase_token", invalid_token)
    with pytest.raises(AuthenticationError):
        await service.exchange_supabase_token(
            "bad", user_agent=None, ip_address=None
        )


@pytest.mark.asyncio
async def test_supabase_verifier_dispatch_and_jwks_cache(monkeypatch):
    real_supabase_jwk = security._supabase_jwk
    monkeypatch.setattr(settings, "supabase_url", None)
    with pytest.raises(ValueError, match="not configured"):
        await security.decode_supabase_token("token")

    monkeypatch.setattr(settings, "supabase_url", "https://project.supabase.co")
    monkeypatch.setattr(settings, "supabase_jwt_secret", None)
    monkeypatch.setattr(settings, "supabase_publishable_key", None)
    monkeypatch.setattr(
        security.jwt, "get_unverified_header", lambda _: {"alg": "HS512"}
    )
    with pytest.raises(ValueError, match="Unsupported"):
        await security.decode_supabase_token("token")

    async def fake_jwk(key_id):
        assert key_id == "key-1"
        return {"kid": key_id}

    monkeypatch.setattr(security, "_supabase_jwk", fake_jwk)
    monkeypatch.setattr(
        security.jwt,
        "get_unverified_header",
        lambda _: {"alg": "RS256", "kid": "key-1"},
    )
    monkeypatch.setattr(
        security,
        "_decode_supabase_jwt",
        lambda token, key, algorithm: {"sub": "verified", "alg": algorithm},
    )
    assert (await security.decode_supabase_token("token"))["alg"] == "RS256"
    monkeypatch.setattr(security, "_supabase_jwk", real_supabase_jwk)

    async def cached_jwks(_):
        return {"keys": [{"kid": "cached", "kty": "RSA"}]}

    monkeypatch.setattr(security.cache, "get_json", cached_jwks)
    assert (await security._supabase_jwk("cached"))["kty"] == "RSA"
    with pytest.raises(ValueError, match="not found"):
        await security._supabase_jwk("missing")
    with pytest.raises(ValueError, match="missing a key ID"):
        await security._supabase_jwk(None)


@pytest.mark.asyncio
async def test_supabase_auth_server_fallback(monkeypatch):
    monkeypatch.setattr(settings, "supabase_url", "https://project.supabase.co")
    monkeypatch.setattr(settings, "supabase_publishable_key", "sb_publishable_test")

    class Response:
        def __init__(self, status_code):
            self.status_code = status_code

        def json(self):
            return {
                "id": str(uuid4()),
                "email": "server@example.com",
                "email_confirmed_at": "2026-01-01T00:00:00Z",
                "user_metadata": {"name": "Server User"},
            }

    class Client:
        def __init__(self, response):
            self.response = response

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, headers):
            assert headers["apikey"] == "sb_publishable_test"
            return self.response

    monkeypatch.setattr(
        security.httpx, "AsyncClient", lambda timeout: Client(Response(200))
    )
    payload = await security._verify_supabase_with_auth_server("token")
    assert payload["email"] == "server@example.com"

    monkeypatch.setattr(
        security.httpx, "AsyncClient", lambda timeout: Client(Response(401))
    )
    with pytest.raises(ValueError, match="rejected"):
        await security._verify_supabase_with_auth_server("token")
