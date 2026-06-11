from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operations import HelperSheet
from app.repositories.operations import OperationsRepository
from app.utils.serialization import model_dict


class HelperSheetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.operations = OperationsRepository(session)

    async def create(self, user_id: UUID, title: str, data: dict, scheme_id: UUID | None = None) -> dict:
        entity = HelperSheet(user_id=user_id, title=title, data=data, scheme_id=scheme_id)
        result = await self.operations.add_helper_sheet(entity)
        await self.session.commit()
        return model_dict(result)

    async def get(self, user_id: UUID, sheet_id: UUID) -> dict | None:
        row = await self.operations.get_helper_sheet(user_id, sheet_id)
        return model_dict(row) if row else None

    async def list(self, user_id: UUID, limit: int = 100, offset: int = 0) -> list[dict]:
        rows = await self.operations.list_helper_sheets(user_id, limit=limit, offset=offset)
        return [model_dict(row) for row in rows]

    async def delete(self, user_id: UUID, sheet_id: UUID) -> None:
        await self.operations.delete_helper_sheet(user_id, sheet_id)
        await self.session.commit()
