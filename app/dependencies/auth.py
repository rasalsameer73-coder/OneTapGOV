from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError
from app.core.security import decode_token, decode_supabase_token
from app.core.config import settings
from app.models.identity import User
from app.repositories.users import UserRepository

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    user: User
    role: str


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db_session),
) -> Principal:
    if credentials is None:
        raise AuthenticationError("Bearer token is required")
    # First try internal access token
    try:
        payload = decode_token(credentials.credentials, "access")
        user_id = UUID(payload["sub"])
        repository = UserRepository(session)
        user = await repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User account is unavailable")
        role = await repository.get_role_name(user)
        return Principal(user=user, role=role)
    except Exception:
        # Fall back to Supabase token verification using JWT verification helper
        try:
            payload = await decode_supabase_token(credentials.credentials)
        except Exception:
            raise AuthenticationError("Invalid access token")

        supabase_id = None
        email = None
        try:
            if payload.get("sub"):
                supabase_id = UUID(str(payload.get("sub")))
        except Exception:
            supabase_id = None
        email = payload.get("email")

        repository = UserRepository(session)
        user = None
        if supabase_id is not None:
            user = await repository.get_by_supabase_id(supabase_id)
        if user is None and email:
            user = await repository.get_by_email(email)

        # Create a local user mapping if necessary
        if user is None:
            role_obj = await repository.get_role("citizen")
            if role_obj is None:
                raise AuthenticationError("User role not available")
            user = await repository.create(
                email=email or "",
                role_id=role_obj.id,
                password_hash=None,
                supabase_user_id=supabase_id,
                is_verified=bool(payload.get("email_confirmed_at") or payload.get("email_confirmed")),
            )
        else:
            # ensure supabase id is recorded
            if supabase_id is not None and getattr(user, "supabase_user_id", None) is None:
                user.supabase_user_id = supabase_id
                await session.flush()

        if not user.is_active:
            raise AuthenticationError("User account is unavailable")
        role = await repository.get_role_name(user)
        return Principal(user=user, role=role)
