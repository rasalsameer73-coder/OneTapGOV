from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.extraction import ExtractionRequest
from app.services.extraction import AIExtractionService

router = APIRouter(prefix="/ai", tags=["AI Extraction"])


@router.post("/extract")
async def extract_profile(
    payload: ExtractionRequest,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    result = await AIExtractionService(session).extract(principal.user.id, payload.text)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Information extracted; no eligibility decision was made",
        trace_id=request.state.trace_id,
    )

