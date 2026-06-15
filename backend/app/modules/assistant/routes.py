from fastapi import APIRouter

from app.modules.assistant.schemas import (
    AssistantQuery,
    AssistantResponse,
)

from app.modules.assistant.service import (
    AssistantService,
)

router = APIRouter()


@router.post(
    "",
    response_model=AssistantResponse,
)
async def ask_assistant(
    query: AssistantQuery,
):

    service = AssistantService()

    return await service.answer_question(
        query.question
    )