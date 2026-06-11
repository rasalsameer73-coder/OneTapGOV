from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.schemes import SchemeRepository
from app.repositories.operations import OperationsRepository
from app.utils.serialization import model_dict


class SavedSchemeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schemes = SchemeRepository(session)
        self.operations = OperationsRepository(session)

    async def create(self, user_id: UUID, scheme_id: UUID) -> dict:
        scheme = await self.schemes.get(scheme_id)
        if scheme is None or not scheme.is_active:
            raise NotFoundError("Scheme not found or inactive")
        entity = await self.operations.add_saved_scheme(user_id, scheme_id)
        await self.session.commit()
        return model_dict(entity)

    async def delete(self, user_id: UUID, scheme_id: UUID) -> None:
        await self.operations.remove_saved_scheme(user_id, scheme_id)
        await self.session.commit()

    async def list(self, user_id: UUID, limit: int = 100, offset: int = 0) -> list[dict]:
        rows = await self.operations.list_saved_schemes(user_id, limit=limit, offset=offset)
        return [model_dict(row) for row in rows]
