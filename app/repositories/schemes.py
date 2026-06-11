from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemes import (
    EligibilityRule,
    RequiredDocument,
    RuleVersion,
    Scheme,
    SchemeVersion,
)


class SchemeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_active(self, limit: int = 100, offset: int = 0) -> tuple[list[Scheme], int]:
        where = Scheme.is_active.is_(True)
        total = await self.session.scalar(select(func.count()).select_from(Scheme).where(where))
        result = await self.session.scalars(
            select(Scheme)
            .where(where)
            .order_by(Scheme.priority.asc(), Scheme.code.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result), int(total or 0)

    async def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[Scheme], int]:
        total = await self.session.scalar(select(func.count()).select_from(Scheme))
        result = await self.session.scalars(
            select(Scheme)
            .order_by(Scheme.priority.asc(), Scheme.code.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result), int(total or 0)

    async def get(self, scheme_id: UUID) -> Scheme | None:
        return await self.session.get(Scheme, scheme_id)

    async def get_by_code(self, code: str) -> Scheme | None:
        return await self.session.scalar(select(Scheme).where(Scheme.code == code))

    async def get_current_version(self, scheme: Scheme) -> SchemeVersion | None:
        return await self.session.scalar(
            select(SchemeVersion).where(
                SchemeVersion.scheme_id == scheme.id,
                SchemeVersion.version_number == scheme.current_version,
            )
        )

    async def get_rules(self, scheme_id: UUID) -> list[tuple[EligibilityRule, RuleVersion]]:
        rows = await self.session.execute(
            select(EligibilityRule, RuleVersion)
            .join(
                RuleVersion,
                (RuleVersion.rule_id == EligibilityRule.id)
                & (RuleVersion.version_number == EligibilityRule.current_version),
            )
            .where(
                EligibilityRule.scheme_id == scheme_id,
                EligibilityRule.is_active.is_(True),
                RuleVersion.is_active.is_(True),
            )
            .order_by(EligibilityRule.priority.asc(), EligibilityRule.code.asc())
        )
        return list(rows.tuples())

    async def get_documents(self, scheme_id: UUID) -> list[RequiredDocument]:
        result = await self.session.scalars(
            select(RequiredDocument)
            .where(
                RequiredDocument.scheme_id == scheme_id,
                RequiredDocument.is_active.is_(True),
            )
            .order_by(RequiredDocument.weight.desc(), RequiredDocument.code.asc())
        )
        return list(result)

    async def create_scheme(self, scheme: Scheme, version: SchemeVersion) -> Scheme:
        self.session.add(scheme)
        await self.session.flush()
        version.scheme_id = scheme.id
        self.session.add(version)
        await self.session.flush()
        return scheme

    async def add_rule(self, rule: EligibilityRule, version: RuleVersion) -> EligibilityRule:
        self.session.add(rule)
        await self.session.flush()
        version.rule_id = rule.id
        self.session.add(version)
        await self.session.flush()
        return rule

    async def add_rule_version(
        self, rule: EligibilityRule, version: RuleVersion
    ) -> RuleVersion:
        previous = await self.session.scalar(
            select(RuleVersion).where(
                RuleVersion.rule_id == rule.id,
                RuleVersion.is_active.is_(True),
            )
        )
        if previous:
            previous.is_active = False
        self.session.add(version)
        rule.current_version = version.version_number
        await self.session.flush()
        return version

    async def get_rule(self, rule_id: UUID) -> EligibilityRule | None:
        return await self.session.get(EligibilityRule, rule_id)

