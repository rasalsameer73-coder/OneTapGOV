from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agriculture.models import AgricultureProfile


class AgricultureRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> AgricultureProfile | None:

        result = await self.db.execute(
            select(AgricultureProfile).where(
                AgricultureProfile.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create_profile(
        self,
        profile: AgricultureProfile,
    ) -> AgricultureProfile:

        self.db.add(profile)

        await self.db.commit()

        await self.db.refresh(profile)

        return profile

    async def update_profile(
        self,
        profile: AgricultureProfile,
    ) -> AgricultureProfile:

        await self.db.commit()

        await self.db.refresh(profile)

        return profile