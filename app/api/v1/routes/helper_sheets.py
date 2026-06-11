from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.common import success_response
from app.services.helper_sheets import HelperSheetService

router = APIRouter(prefix="/helper-sheets", tags=["Helper Sheets"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_helper_sheet(
    payload: dict,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    title = payload.get("title", "Helper Sheet")
    data = payload.get("data", {})
    scheme_id = payload.get("scheme_id")
    entity = await HelperSheetService(session).create(principal.user.id, title, data, scheme_id)
    return success_response(data=entity, message="Helper sheet created", trace_id=request.state.trace_id)


@router.get("")
async def list_helper_sheets(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await HelperSheetService(session).list(principal.user.id)
    return success_response(data=data, message="Helper sheets retrieved", trace_id=request.state.trace_id)


@router.get("/{sheet_id}")
async def get_helper_sheet(
    sheet_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await HelperSheetService(session).get(principal.user.id, sheet_id)
    return success_response(data=data, message="Helper sheet retrieved", trace_id=request.state.trace_id)


@router.delete("/{sheet_id}")
async def delete_helper_sheet(
    sheet_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    await HelperSheetService(session).delete(principal.user.id, sheet_id)
    return success_response(data=None, message="Helper sheet deleted", trace_id=request.state.trace_id)
