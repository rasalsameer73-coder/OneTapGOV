from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    SupabaseExchangeRequest,
)
from app.schemas.common import success_response
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _client(request: Request) -> tuple[str | None, str | None]:
    return request.headers.get("user-agent"), request.client.host if request.client else None


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    user_agent, ip_address = _client(request)
    user, tokens = await AuthService(session).register(
        payload, user_agent=user_agent, ip_address=ip_address
    )
    return success_response(
        data={
            "user": {"id": str(user.id), "email": user.email, "role": "citizen"},
            "tokens": tokens.model_dump(),
        },
        message="Registration successful",
        trace_id=request.state.trace_id,
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    user_agent, ip_address = _client(request)
    user, tokens = await AuthService(session).login(
        payload, user_agent=user_agent, ip_address=ip_address
    )
    return success_response(
        data={"user": {"id": str(user.id), "email": user.email}, "tokens": tokens.model_dump()},
        message="Login successful",
        trace_id=request.state.trace_id,
    )


@router.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    user_agent, ip_address = _client(request)
    tokens = await AuthService(session).refresh(
        payload.refresh_token, user_agent=user_agent, ip_address=ip_address
    )
    return success_response(
        data=tokens.model_dump(),
        message="Tokens rotated",
        trace_id=request.state.trace_id,
    )


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    await AuthService(session).logout(payload.refresh_token)
    return success_response(
        data=None, message="Logged out", trace_id=request.state.trace_id
    )


@router.post("/supabase/exchange")
async def exchange_supabase_token(
    payload: SupabaseExchangeRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    user_agent, ip_address = _client(request)
    user, tokens = await AuthService(session).exchange_supabase_token(
        payload.access_token, user_agent=user_agent, ip_address=ip_address
    )
    return success_response(
        data={"user": {"id": str(user.id), "email": user.email}, "tokens": tokens.model_dump()},
        message="Supabase identity linked",
        trace_id=request.state.trace_id,
    )


@router.get("/me")
async def me(request: Request, principal: Principal = Depends(get_current_principal)):
    return success_response(
        data={
            "id": str(principal.user.id),
            "email": principal.user.email,
            "role": principal.role,
            "is_verified": principal.user.is_verified,
        },
        message="Current user",
        trace_id=request.state.trace_id,
    )

