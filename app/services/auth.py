from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_supabase_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.enums import RoleName
from app.models.identity import RefreshToken
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from app.utils.sanitization import normalize_email, sanitize_text


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(
        self, request: RegisterRequest, *, user_agent: str | None, ip_address: str | None
    ) -> tuple[object, TokenPair]:
        email = normalize_email(str(request.email))
        if await self.users.get_by_email(email):
            raise ConflictError("An account with this email already exists")
        role = await self.users.get_role(RoleName.CITIZEN)
        if role is None:
            raise RuntimeError("Citizen role has not been seeded")
        user = await self.users.create(
            email=email,
            role_id=role.id,
            password_hash=hash_password(request.password),
        )
        await self.users.ensure_profile(user.id, sanitize_text(request.name))
        tokens = await self._issue_pair(user, role.name, user_agent, ip_address)
        await self.session.commit()
        return user, tokens

    async def login(
        self, request: LoginRequest, *, user_agent: str | None, ip_address: str | None
    ) -> tuple[object, TokenPair]:
        user = await self.users.get_by_email(normalize_email(str(request.email)))
        if (
            user is None
            or not user.password_hash
            or not verify_password(request.password, user.password_hash)
            or not user.is_active
        ):
            raise AuthenticationError("Invalid email or password")
        user.last_login_at = datetime.now(UTC)
        role = await self.users.get_role_name(user)
        tokens = await self._issue_pair(user, role, user_agent, ip_address)
        await self.session.commit()
        return user, tokens

    async def exchange_supabase_token(
        self, token: str, *, user_agent: str | None, ip_address: str | None
    ) -> tuple[object, TokenPair]:
        try:
            payload = await decode_supabase_token(token)
            supabase_id = UUID(payload["sub"])
            email = normalize_email(payload["email"])
        except (ValueError, KeyError) as exc:
            raise AuthenticationError("Invalid Supabase access token") from exc
        user = await self.users.get_by_supabase_id(supabase_id)
        if user is None:
            existing = await self.users.get_by_email(email)
            if existing and existing.supabase_user_id not in (None, supabase_id):
                raise ConflictError("Email is already linked to another identity")
            if existing:
                user = existing
                user.supabase_user_id = supabase_id
                user.is_verified = bool(payload.get("email_confirmed_at"))
            else:
                role = await self.users.get_role(RoleName.CITIZEN)
                if role is None:
                    raise RuntimeError("Citizen role has not been seeded")
                user = await self.users.create(
                    email=email,
                    role_id=role.id,
                    password_hash=None,
                    supabase_user_id=supabase_id,
                    is_verified=bool(payload.get("email_confirmed_at")),
                )
                await self.users.ensure_profile(
                    user.id, payload.get("user_metadata", {}).get("name")
                )
        role_name = await self.users.get_role_name(user)
        tokens = await self._issue_pair(user, role_name, user_agent, ip_address)
        await self.session.commit()
        return user, tokens

    async def refresh(
        self, token: str, *, user_agent: str | None, ip_address: str | None
    ) -> TokenPair:
        try:
            payload = decode_token(token, "refresh")
            token_hash = hash_token(payload["jti"])
            family_id = UUID(payload["family"])
            user_id = UUID(payload["sub"])
        except (ValueError, KeyError) as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        stored = await self.users.get_refresh_token(token_hash)
        if stored is None or stored.family_id != family_id:
            raise AuthenticationError("Refresh token was not issued by this service")
        if stored.revoked_at is not None:
            await self.users.revoke_token_family(family_id)
            await self.session.commit()
            raise AuthenticationError("Refresh token reuse detected")
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            raise AuthenticationError("Refresh token has expired")
        user = await self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User account is unavailable")
        role = await self.users.get_role_name(user)
        stored.revoked_at = datetime.now(UTC)
        pair = await self._issue_pair(
            user, role, user_agent, ip_address, family_id=family_id
        )
        replacement = await self.users.get_refresh_token(
            hash_token(decode_token(pair.refresh_token, "refresh")["jti"])
        )
        stored.replaced_by_id = replacement.id if replacement else None
        await self.session.commit()
        return pair

    async def logout(self, token: str) -> None:
        try:
            payload = decode_token(token, "refresh")
            stored = await self.users.get_refresh_token(hash_token(payload["jti"]))
        except (ValueError, KeyError) as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.now(UTC)
            await self.session.commit()

    async def _issue_pair(
        self,
        user,
        role: str,
        user_agent: str | None,
        ip_address: str | None,
        family_id: UUID | None = None,
    ) -> TokenPair:
        access_token, expires_in = create_access_token(user.id, role)
        family = family_id or uuid4()
        refresh_token, token_hash, expires_at = create_refresh_token(user.id, family)
        await self.users.add_refresh_token(
            RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                family_id=family,
                expires_at=expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
