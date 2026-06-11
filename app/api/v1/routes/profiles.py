from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.profile import CompleteProfileUpdate
from app.services.profiles import ProfileService

router = APIRouter(prefix="/profiles", tags=["User Profile"])


@router.get("/me")
async def get_profile(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await ProfileService(session).get(principal.user.id)
    return success_response(
        data=data, message="Profile retrieved", trace_id=request.state.trace_id
    )


@router.patch("/me")
async def update_profile(
    payload: CompleteProfileUpdate,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await ProfileService(session).update(principal.user.id, payload)
    return success_response(
        data=data, message="Profile updated", trace_id=request.state.trace_id
    )

