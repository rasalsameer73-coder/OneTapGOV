from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operations import (
    ActionPlan,
    AuditLog,
    EligibilityDecision,
    Notification,
    Recommendation,
    UserDocument,
)


class OperationsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, entity):
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def list_user_documents(self, user_id: UUID) -> list[UserDocument]:
        result = await self.session.scalars(
            select(UserDocument)
            .where(UserDocument.user_id == user_id)
            .order_by(UserDocument.updated_at.desc())
        )
        return list(result)

    async def get_user_document(self, user_id: UUID, document_id: UUID) -> UserDocument | None:
        return await self.session.scalar(
            select(UserDocument).where(
                UserDocument.id == document_id,
                UserDocument.user_id == user_id,
            )
        )

    async def replace_recommendations(
        self, user_id: UUID, recommendations: list[Recommendation]
    ) -> None:
        await self.session.execute(
            delete(Recommendation).where(Recommendation.user_id == user_id)
        )
        self.session.add_all(recommendations)
        await self.session.flush()

    async def list_recommendations(self, user_id: UUID) -> list[Recommendation]:
        result = await self.session.scalars(
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.priority_score.desc())
        )
        return list(result)

    async def add_saved_scheme(self, user_id: UUID, scheme_id: UUID):
        from app.models.operations import SavedScheme

        entity = SavedScheme(user_id=user_id, scheme_id=scheme_id)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def remove_saved_scheme(self, user_id: UUID, scheme_id: UUID) -> None:
        from app.models.operations import SavedScheme

        await self.session.execute(
            delete(SavedScheme).where(SavedScheme.user_id == user_id, SavedScheme.scheme_id == scheme_id)
        )
        await self.session.flush()

    async def list_saved_schemes(self, user_id: UUID, limit: int = 100, offset: int = 0) -> list:
        from app.models.operations import SavedScheme

        result = await self.session.scalars(
            select(SavedScheme)
            .where(SavedScheme.user_id == user_id)
            .order_by(SavedScheme.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result)

    async def list_notifications(self, user_id: UUID, limit: int = 50) -> list[Notification]:
        result = await self.session.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result)

    async def list_audit_logs(self, limit: int, offset: int) -> list[AuditLog]:
        result = await self.session.scalars(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result)

    async def add_helper_sheet(self, helper_sheet):
        self.session.add(helper_sheet)
        await self.session.flush()
        return helper_sheet

    async def get_helper_sheet(self, user_id: UUID, sheet_id: UUID):
        from app.models.operations import HelperSheet

        return await self.session.scalar(
            select(HelperSheet).where(HelperSheet.id == sheet_id, HelperSheet.user_id == user_id)
        )

    async def list_helper_sheets(self, user_id: UUID, limit: int = 100, offset: int = 0):
        from app.models.operations import HelperSheet

        result = await self.session.scalars(
            select(HelperSheet)
            .where(HelperSheet.user_id == user_id)
            .order_by(HelperSheet.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result)

    async def delete_helper_sheet(self, user_id: UUID, sheet_id: UUID) -> None:
        from app.models.operations import HelperSheet

        await self.session.execute(
            delete(HelperSheet).where(HelperSheet.id == sheet_id, HelperSheet.user_id == user_id)
        )
        await self.session.flush()

