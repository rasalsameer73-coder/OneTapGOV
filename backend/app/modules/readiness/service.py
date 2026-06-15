from app.modules.documents.repository import (
    DocumentRepository,
)

from app.modules.user_documents.repository import (
    UserDocumentRepository,
)

from app.modules.readiness.schemas import (
    ReadinessResponse,
)


class ReadinessService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        user_document_repository: UserDocumentRepository,
    ):

        self.document_repository = document_repository

        self.user_document_repository = user_document_repository

    async def get_readiness(
        self,
        current_user,
        scheme_id: int,
        scheme_name: str,
    ) -> ReadinessResponse:

        required_docs = (
            await self.document_repository.get_documents_by_scheme_id(
                scheme_id
            )
        )

        uploaded_docs = (
            await self.user_document_repository.get_user_documents(
                current_user.id
            )
        )

        required_documents = [
            doc.document_name
            for doc in required_docs
        ]

        uploaded_documents = [
            doc.document_name
            for doc in uploaded_docs
        ]

        missing_documents = [
            document
            for document in required_documents
            if document not in uploaded_documents
        ]

        if len(required_documents) == 0:

            readiness_score = 100

        else:

            readiness_score = int(
                (
                    len(uploaded_documents)
                    - len(missing_documents)
                )
                / len(required_documents)
                * 100
            )

            readiness_score = max(
                readiness_score,
                0,
            )

        estimated_completion_days = (
            len(missing_documents)
        )

        next_steps = [
            f"Obtain {document}"
            for document in missing_documents
        ]

        next_steps.append(
            "Submit application"
        )

        return ReadinessResponse(
            scheme_id=scheme_id,

            scheme_name=scheme_name,

            required_documents=required_documents,

            uploaded_documents=uploaded_documents,

            missing_documents=missing_documents,

            readiness_score=readiness_score,

            estimated_completion_days=estimated_completion_days,

            next_steps=next_steps,
        )