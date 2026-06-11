from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.notifications import NotificationCreate
from app.services.notifications import NotificationService
from app.utils.serialization import model_dict

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def queue_notification(
    payload: NotificationCreate,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    notification = await NotificationService(session).queue(
        user_id=principal.user.id,
        channel=payload.channel,
        recipient=payload.recipient,
        template_code=payload.template_code,
        payload=payload.payload,
    )
    return success_response(
        data=model_dict(notification),
        message="Notification queued",
        trace_id=request.state.trace_id,
    )


@router.get("")
async def list_notifications(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    rows = await NotificationService(session).list(principal.user.id)
    return success_response(
        data=[model_dict(item) for item in rows],
        message="Notifications retrieved",
        trace_id=request.state.trace_id,
    )
