from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.women.models import WomenProfile


class WomenRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> WomenProfile | None:

        result = await self.db.execute(
            select(WomenProfile).where(
                WomenProfile.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create_profile(
        self,
        profile: WomenProfile,
    ) -> WomenProfile:

        self.db.add(profile)

        await self.db.commit()

        await self.db.refresh(profile)

        return profile

    async def update_profile(
        self,
        profile: WomenProfile,
    ) -> WomenProfile:

        await self.db.commit()

        await self.db.refresh(profile)

        return profile