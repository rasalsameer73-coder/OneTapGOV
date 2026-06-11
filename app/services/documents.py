from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.engines.readiness import ReadinessEngine
from app.models.enums import DocumentStatus
from app.models.operations import UserDocument
from app.repositories.operations import OperationsRepository
from app.repositories.schemes import SchemeRepository
from app.schemas.documents import DocumentStatusUpdate, UserDocumentCreate
from app.utils.sanitization import sanitize_text


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.operations = OperationsRepository(session)
        self.schemes = SchemeRepository(session)
        self.engine = ReadinessEngine()

    async def create(self, user_id: UUID, request: UserDocumentCreate) -> UserDocument:
        document = await self.operations.add(
            UserDocument(
                user_id=user_id,
                document_code=sanitize_text(request.document_code).upper(),
                name=sanitize_text(request.name),
                storage_key=request.storage_key,
                issued_at=request.issued_at,
                expires_at=request.expires_at,
                document_metadata=request.metadata,
                status=DocumentStatus.UPLOADED,
            )
        )
        await self.session.commit()
        return document

    async def list(self, user_id: UUID) -> list[UserDocument]:
        return await self.operations.list_user_documents(user_id)

    async def update_status(
        self, user_id: UUID, document_id: UUID, request: DocumentStatusUpdate
    ) -> UserDocument:
        document = await self.operations.get_user_document(user_id, document_id)
        if document is None:
            raise NotFoundError("Document not found")
        document.status = request.status
        document.rejection_reason = request.rejection_reason
        document.verified_at = (
            datetime.now(UTC) if request.status == DocumentStatus.VERIFIED else None
        )
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def readiness(self, user_id: UUID, scheme_id: UUID) -> dict:
        scheme = await self.schemes.get(scheme_id)
        if scheme is None or not scheme.is_active:
            raise NotFoundError("Scheme not found or inactive")
        requirements = await self.schemes.get_documents(scheme_id)
        documents = await self.operations.list_user_documents(user_id)
        result = self.engine.calculate(requirements, documents)
        result["scheme_id"] = str(scheme_id)
        return result
