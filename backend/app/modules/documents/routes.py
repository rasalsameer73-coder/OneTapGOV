from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.modules.documents.repository import (
    DocumentRepository,
)
from app.modules.documents.schemas import (
    SchemeDocumentCreate,
    SchemeDocumentResponse,
)
from app.modules.documents.service import (
    DocumentService,
)

router = APIRouter()


@router.post(
    "",
    response_model=SchemeDocumentResponse,
)
async def create_document(
    document_data: SchemeDocumentCreate,
    db: AsyncSession = Depends(get_db),
):

    repository = DocumentRepository(db)

    service = DocumentService(
        repository
    )

    return await service.create_document(
        document_data
    )


@router.get(
    "/{scheme_id}",
    response_model=list[
        SchemeDocumentResponse
    ],
)
async def get_documents(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
):

    repository = DocumentRepository(db)

    service = DocumentService(
        repository
    )

    return await service.get_documents_by_scheme_id(
        scheme_id
    )