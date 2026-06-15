from app.modules.user_documents.models import (
    UserDocument,
)

from app.modules.user_documents.repository import (
    UserDocumentRepository,
)

from app.modules.user_documents.schemas import (
    UserDocumentCreate,
)


class UserDocumentService:

    def __init__(
        self,
        repository: UserDocumentRepository,
    ):
        self.repository = repository

    async def create_document(
        self,
        current_user,
        document_data: UserDocumentCreate,
    ):

        document = UserDocument(
            user_id=current_user.id,
            document_name=document_data.document_name,
            file_url=document_data.file_url,
        )

        return await self.repository.create_document(
            document
        )

    async def get_user_documents(
        self,
        current_user,
    ):

        return await self.repository.get_user_documents(
            current_user.id
        )