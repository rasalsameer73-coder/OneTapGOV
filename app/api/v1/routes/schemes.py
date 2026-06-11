from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.common import success_response
from app.services.schemes import SchemeQueryService

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("")
async def list_schemes(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    data = await SchemeQueryService(session).list(limit=limit, offset=offset)
    return success_response(
        data=data, message="Schemes retrieved", trace_id=request.state.trace_id
    )


@router.get("/{scheme_id}")
async def scheme_detail(
    scheme_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    data = await SchemeQueryService(session).detail(scheme_id)
    return success_response(
        data=data, message="Scheme retrieved", trace_id=request.state.trace_id
    )

