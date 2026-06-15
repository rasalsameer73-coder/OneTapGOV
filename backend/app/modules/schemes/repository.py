from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.schemes.models import (
    Scheme,
    SchemeVersion,
    EligibilityRule,
    RuleCondition,
)


class SchemeRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_scheme(
        self,
        scheme: Scheme,
    ) -> Scheme:

        self.db.add(scheme)

        await self.db.commit()

        await self.db.refresh(scheme)

        return scheme

    async def get_scheme_by_id(
        self,
        scheme_id: int,
    ) -> Scheme | None:

        result = await self.db.execute(
            select(Scheme).where(
                Scheme.id == scheme_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all_schemes(
        self,
    ):

        result = await self.db.execute(
            select(Scheme)
        )

        return result.scalars().all()

    async def update_scheme(
        self,
        scheme: Scheme,
    ):

        await self.db.commit()

        await self.db.refresh(scheme)

        return scheme

    async def get_scheme_versions(
        self,
        scheme_id: int,
    ):

        result = await self.db.execute(
            select(
                SchemeVersion
            ).where(
                SchemeVersion.scheme_id == scheme_id
            )
        )

        return result.scalars().all()

    async def get_eligibility_rules(
        self,
        version_id: int,
    ):

        result = await self.db.execute(
            select(
                EligibilityRule
            ).where(
                EligibilityRule.scheme_version_id == version_id
            )
        )

        return result.scalars().all()

    async def get_rule_conditions(
        self,
        rule_id: int,
    ):

        result = await self.db.execute(
            select(
                RuleCondition
            ).where(
                RuleCondition.eligibility_rule_id == rule_id
            )
        )

        return result.scalars().all()