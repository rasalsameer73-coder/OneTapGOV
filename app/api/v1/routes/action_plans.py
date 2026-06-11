from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.services.action_plans import ActionPlanService
from app.utils.serialization import model_dict

router = APIRouter(prefix="/action-plans", tags=["Action Plans"])


@router.post("/generate/{scheme_id}")
async def generate(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    plan = await ActionPlanService(session).generate(principal.user.id, scheme_id)
    return success_response(
        data=model_dict(plan),
        message="Action plan generated",
        trace_id=request.state.trace_id,
    )

