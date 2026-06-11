from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate")
async def generate(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await RecommendationService(session).generate(principal.user.id)
    return success_response(
        data=data, message="Recommendations generated", trace_id=request.state.trace_id
    )


@router.get("")
async def list_recommendations(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await RecommendationService(session).list(principal.user.id)
    return success_response(
        data=data, message="Recommendations retrieved", trace_id=request.state.trace_id
    )

