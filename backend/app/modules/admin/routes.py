from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.modules.schemes.models import (
    Scheme,
    SchemeVersion,
    EligibilityRule,
    RuleCondition,
)

from app.modules.documents.models import (
    SchemeDocument,
)

router = APIRouter()


@router.post("/scheme")
async def create_scheme(
    scheme_name: str,
    scheme_code: str,
    db: AsyncSession = Depends(get_db),
):

    scheme = Scheme(
        scheme_name=scheme_name,
        scheme_code=scheme_code,
    )

    db.add(scheme)

    await db.commit()

    await db.refresh(scheme)

    return scheme


@router.post("/version")
async def create_version(
    scheme_id: int,
    version_number: int,
    db: AsyncSession = Depends(get_db),
):

    version = SchemeVersion(
        scheme_id=scheme_id,
        version_number=version_number,
    )

    db.add(version)

    await db.commit()

    await db.refresh(version)

    return version


@router.post("/rule")
async def create_rule(
    scheme_version_id: int,
    rule_name: str,
    db: AsyncSession = Depends(get_db),
):

    rule = EligibilityRule(
        scheme_version_id=scheme_version_id,
        rule_name=rule_name,
    )

    db.add(rule)

    await db.commit()

    await db.refresh(rule)

    return rule


@router.post("/condition")
async def create_condition(
    eligibility_rule_id: int,
    field_name: str,
    comparison_operator: str,
    comparison_value: str,
    human_readable_condition: str,
    db: AsyncSession = Depends(get_db),
):

    condition = RuleCondition(
        eligibility_rule_id=eligibility_rule_id,
        field_name=field_name,
        comparison_operator=comparison_operator,
        comparison_value=comparison_value,
        human_readable_condition=human_readable_condition,
    )

    db.add(condition)

    await db.commit()

    await db.refresh(condition)

    return condition


@router.post("/document")
async def create_document(
    scheme_id: int,
    document_name: str,
    db: AsyncSession = Depends(get_db),
):

    document = SchemeDocument(
        scheme_id=scheme_id,
        document_name=document_name,
    )

    db.add(document)

    await db.commit()

    await db.refresh(document)

    return document