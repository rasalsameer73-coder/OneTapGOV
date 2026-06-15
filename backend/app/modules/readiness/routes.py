from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.database import (
    get_db,
)

from app.modules.auth.dependencies import (
    get_current_user,
)

from app.modules.documents.repository import (
    DocumentRepository,
)

from app.modules.user_documents.repository import (
    UserDocumentRepository,
)

from app.modules.readiness.schemas import (
    ReadinessResponse,
)

from app.modules.readiness.service import (
    ReadinessService,
)

router = APIRouter()


@router.get(
    "/{scheme_id}/{scheme_name}",
    response_model=ReadinessResponse,
)
async def get_readiness(
    scheme_id: int,
    scheme_name: str,
    current_user=Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = ReadinessService(
        document_repository=DocumentRepository(
            db
        ),

        user_document_repository=UserDocumentRepository(
            db
        ),
    )

    return await service.get_readiness(
        current_user,
        scheme_id,
        scheme_name,
    )