from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.schemes import SchemeRepository
from app.utils.serialization import model_dict


class SchemeQueryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = SchemeRepository(session)

    async def list(self, *, limit: int, offset: int, include_inactive: bool = False) -> dict:
        if include_inactive:
            schemes, total = await self.repository.list_all(limit, offset)
        else:
            schemes, total = await self.repository.list_active(limit, offset)
        items = []
        for scheme in schemes:
            if scheme.deleted_at is not None:
                continue
            version = await self.repository.get_current_version(scheme)
            if version is None or (not include_inactive and not version.is_published):
                continue
            items.append(
                {
                    **model_dict(
                        scheme,
                        exclude={"created_at", "updated_at", "deleted_at"},
                    ),
                    "version": model_dict(
                        version,
                        exclude={"scheme_id", "created_at", "updated_at"},
                    ),
                }
            )
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    async def detail(self, scheme_id: UUID) -> dict:
        scheme = await self.repository.get(scheme_id)
        if scheme is None or not scheme.is_active or scheme.deleted_at is not None:
            raise NotFoundError("Scheme not found or inactive")
        version = await self.repository.get_current_version(scheme)
        if version is None or not version.is_published:
            raise NotFoundError("Published scheme version not found")
        documents = await self.repository.get_documents(scheme.id)
        return {
            **model_dict(scheme, exclude={"created_at", "updated_at", "deleted_at"}),
            "version": model_dict(
                version, exclude={"scheme_id", "created_at", "updated_at"}
            ),
            "required_documents": [
                model_dict(item, exclude={"scheme_id", "created_at", "updated_at"})
                for item in documents
            ],
        }

