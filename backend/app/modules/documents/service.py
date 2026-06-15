from app.modules.documents.models import (
    SchemeDocument,
)
from app.modules.documents.repository import (
    DocumentRepository,
)
from app.modules.documents.schemas import (
    SchemeDocumentCreate,
)


class DocumentService:

    def __init__(
        self,
        repository: DocumentRepository,
    ):
        self.repository = repository

    async def create_document(
        self,
        document_data: SchemeDocumentCreate,
    ):

        document = SchemeDocument(
            scheme_id=document_data.scheme_id,
            document_name=document_data.document_name,
            is_mandatory=document_data.is_mandatory,
        )

        return await self.repository.create_document(
            document
        )

    async def get_documents_by_scheme_id(
        self,
        scheme_id: int,
    ):
        return await self.repository.get_documents_by_scheme_id(
            scheme_id
        )