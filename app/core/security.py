import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import httpx
from jose import JWTError, jwt

from app.core.cache import cache
from app.core.config import settings

JWT_ALGORITHM = "HS256"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=64,
    )
    return "scrypt${}${}${}${}${}".format(
        SCRYPT_N,
        SCRYPT_R,
        SCRYPT_P,
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(derived).decode(),
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, n, r, p, salt_b64, expected_b64 = encoded_hash.split("$", 5)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(expected_b64.encode())
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: UUID, role: str) -> tuple[str, int]:
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=settings.access_token_ttl_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "iss": "onetapgov",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM), int(
        (expires - now).total_seconds()
    )


def create_refresh_token(user_id: UUID, family_id: UUID) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    expires = now + timedelta(days=settings.refresh_token_ttl_days)
    token_id = secrets.token_urlsafe(32)
    payload = {
        "sub": str(user_id),
        "jti": token_id,
        "family": str(family_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "iss": "onetapgov",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)
    return token, hash_token(token_id), expires


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
            issuer="onetapgov",
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
    if payload.get("type") != expected_type:
        raise ValueError(f"Expected a {expected_type} token")
    return payload


async def decode_supabase_token(token: str) -> dict[str, Any]:
    if not settings.supabase_url:
        raise ValueError("Supabase authentication is not configured")
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise ValueError("Invalid Supabase token header") from exc
    algorithm = header.get("alg")
    if algorithm in {"ES256", "RS256"}:
        key = await _supabase_jwk(header.get("kid"))
        return _decode_supabase_jwt(token, key, algorithm)
    if algorithm == "HS256" and settings.supabase_publishable_key:
        return await _verify_supabase_with_auth_server(token)
    if algorithm == "HS256" and settings.supabase_jwt_secret:
        return _decode_supabase_jwt(token, settings.supabase_jwt_secret, algorithm)
    raise ValueError("Unsupported or unconfigured Supabase signing algorithm")


def _decode_supabase_jwt(token: str, key: Any, algorithm: str) -> dict[str, Any]:
    options = {"verify_aud": bool(settings.supabase_jwt_audience)}
    kwargs: dict[str, Any] = {"options": options}
    if settings.supabase_jwt_audience:
        kwargs["audience"] = settings.supabase_jwt_audience
    kwargs["issuer"] = settings.supabase_jwt_issuer or (
        f"{settings.supabase_url.rstrip('/')}/auth/v1"
    )
    try:
        return jwt.decode(token, key, algorithms=[algorithm], **kwargs)
    except JWTError as exc:
        raise ValueError("Invalid Supabase token") from exc


async def _supabase_jwk(key_id: str | None) -> dict[str, Any]:
    if not key_id:
        raise ValueError("Supabase token is missing a key ID")
    cache_key = "supabase:jwks"
    jwks = await cache.get_json(cache_key)
    if jwks is None:
        url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            jwks = response.json()
        await cache.set_json(cache_key, jwks, ttl_seconds=600)
    for key in jwks.get("keys", []):
        if key.get("kid") == key_id:
            return key
    raise ValueError("Supabase signing key was not found")


async def _verify_supabase_with_auth_server(token: str) -> dict[str, Any]:
    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "apikey": settings.supabase_publishable_key,
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError("Supabase rejected the token")
    user = response.json()
    return {
        "sub": user["id"],
        "email": user["email"],
        "email_confirmed_at": user.get("email_confirmed_at"),
        "user_metadata": user.get("user_metadata") or {},
    }


def hash_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
