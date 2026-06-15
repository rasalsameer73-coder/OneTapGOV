from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import (
    SchemeDocument,
)
from app.modules.schemes.models import Scheme
from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class DocumentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_document(
        self,
        document: SchemeDocument,
    ):

        # Ensure referenced scheme exists to avoid FK errors
        result = await self.db.execute(
            select(Scheme).where(Scheme.id == document.scheme_id)
        )
        scheme = result.scalar_one_or_none()
        if scheme is None:
            raise HTTPException(status_code=400, detail="scheme_id does not exist")

        self.db.add(document)
        try:
            await self.db.commit()
            await self.db.refresh(document)
            return document
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_documents_by_scheme_id(
        self,
        scheme_id: int,
    ):

        result = await self.db.execute(
            select(
                SchemeDocument
            ).where(
                SchemeDocument.scheme_id == scheme_id
            )
        )

        return result.scalars().all()
    