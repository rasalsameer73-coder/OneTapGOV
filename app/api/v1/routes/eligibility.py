from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.services.eligibility import EligibilityService

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.post("/evaluate/{scheme_id}")
async def evaluate(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    result = await EligibilityService(session).evaluate(principal.user.id, scheme_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Eligibility evaluated by the versioned rule engine",
        trace_id=request.state.trace_id,
    )

