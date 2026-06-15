from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user_documents.models import (
    UserDocument,
)


class UserDocumentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_document(
        self,
        document: UserDocument,
    ):

        self.db.add(document)

        await self.db.commit()

        await self.db.refresh(document)

        return document

    async def get_user_documents(
        self,
        user_id: int,
    ):

        result = await self.db.execute(
            select(
                UserDocument
            ).where(
                UserDocument.user_id == user_id
            )
        )

        return result.scalars().all()