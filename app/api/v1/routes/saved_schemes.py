from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.common import success_response
from app.services.saved_schemes import SavedSchemeService

router = APIRouter(prefix="/saved-schemes", tags=["Saved Schemes"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_saved_scheme(
    payload: dict,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    scheme_id = UUID(payload.get("scheme_id"))
    entity = await SavedSchemeService(session).create(principal.user.id, scheme_id)
    return success_response(data=entity, message="Scheme saved", trace_id=request.state.trace_id)


@router.delete("/{scheme_id}")
async def delete_saved_scheme(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    await SavedSchemeService(session).delete(principal.user.id, scheme_id)
    return success_response(data=None, message="Saved scheme removed", trace_id=request.state.trace_id)


@router.get("")
async def list_saved_schemes(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await SavedSchemeService(session).list(principal.user.id)
    return success_response(data=data, message="Saved schemes retrieved", trace_id=request.state.trace_id)
