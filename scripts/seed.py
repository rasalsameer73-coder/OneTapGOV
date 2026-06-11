import argparse
import asyncio
import os
from decimal import Decimal

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.identity import Admin, Role, User
from app.models.schemes import (
    EligibilityRule,
    RequiredDocument,
    RuleVersion,
    Scheme,
    SchemeVersion,
)


async def seed(admin_email: str | None, admin_password: str | None) -> None:
    async with AsyncSessionFactory() as session:
        roles = {}
        for name, description in (
            (RoleName.CITIZEN, "Citizen using OneTapGOV"),
            (RoleName.ADMIN, "Government scheme administrator"),
        ):
            role = await session.scalar(select(Role).where(Role.name == name))
            if role is None:
                role = Role(name=name, description=description)
                session.add(role)
                await session.flush()
            roles[name] = role

        if admin_email and admin_password:
            admin_user = await session.scalar(select(User).where(User.email == admin_email))
            if admin_user is None:
                admin_user = User(
                    email=admin_email.casefold(),
                    password_hash=hash_password(admin_password),
                    role_id=roles[RoleName.ADMIN].id,
                    is_active=True,
                    is_verified=True,
                )
                session.add(admin_user)
                await session.flush()
                session.add(
                    Admin(
                        user_id=admin_user.id,
                        department="Digital Governance",
                        designation="Platform Administrator",
                    )
                )

        await seed_scheme(
            session,
            code="MH_POST_MATRIC",
            category="Education",
            state="Maharashtra",
            name="Post Matric Scholarship Scheme",
            authority="Government of Maharashtra",
            benefit="Financial support toward tuition fees and maintenance allowance.",
            rules=[
                (
                    "INCOME_LIMIT",
                    "Income below scheme limit",
                    10,
                    {"condition": {"field": "profile.annual_income", "operator": "lt", "value": 200000}},
                    "Annual family income is below the published limit.",
                    "Annual family income is above the published limit.",
                ),
                (
                    "MAHARASHTRA_RESIDENT",
                    "Maharashtra resident",
                    20,
                    {"condition": {"field": "profile.state", "operator": "eq", "value": "Maharashtra"}},
                    "The applicant is a Maharashtra resident.",
                    "The applicant is not recorded as a Maharashtra resident.",
                ),
                (
                    "ACTIVE_STUDENT",
                    "Currently studying",
                    30,
                    {"condition": {"field": "education.is_student", "operator": "eq", "value": True}},
                    "The applicant is currently a student.",
                    "Current student status is not verified.",
                ),
            ],
            documents=[
                ("AADHAAR", "Aadhaar card", Decimal("25")),
                ("MARKSHEET", "Previous marksheet", Decimal("10")),
                ("INCOME_CERT", "Income certificate", Decimal("25")),
                ("DOMICILE", "Domicile certificate", Decimal("20")),
                ("BANK_PASSBOOK", "Bank passbook", Decimal("20")),
            ],
        )
        await session.commit()


async def seed_scheme(
    session,
    *,
    code,
    category,
    state,
    name,
    authority,
    benefit,
    rules,
    documents,
) -> None:
    existing = await session.scalar(select(Scheme).where(Scheme.code == code))
    if existing:
        return
    scheme = Scheme(
        code=code,
        category=category,
        state=state,
        priority=10,
        is_active=True,
        current_version=1,
    )
    session.add(scheme)
    await session.flush()
    session.add(
        SchemeVersion(
            scheme_id=scheme.id,
            version_number=1,
            name=name,
            description=f"Seeded reference configuration for {name}.",
            authority=authority,
            benefit_summary=benefit,
            is_published=True,
            change_note="Initial seed",
        )
    )
    for code_, name_, priority, expression, pass_text, fail_text in rules:
        rule = EligibilityRule(
            scheme_id=scheme.id,
            code=code_,
            name=name_,
            priority=priority,
            current_version=1,
        )
        session.add(rule)
        await session.flush()
        session.add(
            RuleVersion(
                rule_id=rule.id,
                version_number=1,
                expression=expression,
                explanation_pass=pass_text,
                explanation_fail=fail_text,
                is_active=True,
                change_note="Initial seed",
            )
        )
    for code_, name_, weight in documents:
        session.add(
            RequiredDocument(
                scheme_id=scheme.id,
                code=code_,
                name=name_,
                weight=weight,
                is_mandatory=True,
            )
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Seed OneTapGOV reference data")
    parser.add_argument("--admin-email", default=os.getenv("SEED_ADMIN_EMAIL"))
    parser.add_argument("--admin-password", default=os.getenv("SEED_ADMIN_PASSWORD"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if bool(arguments.admin_email) != bool(arguments.admin_password):
        raise SystemExit("Both admin email and admin password must be provided")
    asyncio.run(seed(arguments.admin_email, arguments.admin_password))

