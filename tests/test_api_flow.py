from decimal import Decimal

import pytest

from app.models.schemes import (
    EligibilityRule,
    RequiredDocument,
    RuleVersion,
    Scheme,
    SchemeVersion,
)


async def seed_scheme(session):
    scheme = Scheme(
        code="MH_TEST",
        category="Education",
        state="Maharashtra",
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
            name="Maharashtra Student Benefit",
            description="A test scheme for eligible Maharashtra students.",
            authority="Government of Maharashtra",
            is_published=True,
        )
    )
    for code, priority, expression, pass_text, fail_text in (
        (
            "STATE",
            10,
            {"condition": {"field": "profile.state", "operator": "eq", "value": "Maharashtra"}},
            "Maharashtra resident",
            "Not a Maharashtra resident",
        ),
        (
            "INCOME",
            20,
            {"condition": {"field": "profile.annual_income", "operator": "lt", "value": 200000}},
            "Income is below the limit",
            "Income is above the limit",
        ),
        (
            "STUDENT",
            30,
            {"condition": {"field": "education.is_student", "operator": "eq", "value": True}},
            "Current student",
            "Student status missing",
        ),
    ):
        rule = EligibilityRule(
            scheme_id=scheme.id,
            code=code,
            name=code.title(),
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
            )
        )
    session.add_all(
        [
            RequiredDocument(
                scheme_id=scheme.id,
                code="AADHAAR",
                name="Aadhaar card",
                weight=Decimal("50"),
                is_mandatory=True,
            ),
            RequiredDocument(
                scheme_id=scheme.id,
                code="INCOME_CERT",
                name="Income certificate",
                weight=Decimal("50"),
                is_mandatory=True,
            ),
        ]
    )
    await session.commit()
    return scheme


@pytest.mark.asyncio
async def test_complete_citizen_flow(client, session):
    scheme = await seed_scheme(session)
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "ananya@example.com",
            "password": "StrongPassword12",
            "name": "Ananya Patil",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["success"] is True
    tokens = registration.json()["data"]["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    profile = await client.patch(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "profile": {
                "date_of_birth": "2004-05-01",
                "gender": "female",
                "state": "Maharashtra",
                "district": "Pune",
                "annual_income": 180000,
                "category": "OBC",
            },
            "education": {
                "course": "Engineering",
                "year": 2,
                "marks": 82.5,
                "is_student": True,
            },
        },
    )
    assert profile.status_code == 200
    assert profile.json()["data"]["completion_percentage"] == 100

    extraction = await client.post(
        "/api/v1/ai/extract",
        headers=headers,
        json={"text": "Engineering student from Maharashtra with income ₹1.8 lakh"},
    )
    assert extraction.status_code == 200
    assert extraction.json()["data"]["extracted"]["income"] == "180000.0"

    decision = await client.post(
        f"/api/v1/eligibility/evaluate/{scheme.id}", headers=headers
    )
    assert decision.status_code == 200
    body = decision.json()["data"]
    assert body["status"] == "eligible"
    assert len(body["eligible_because"]) == 3
    assert len(body["ruleset_fingerprint"]) == 64

    document = await client.post(
        "/api/v1/documents",
        headers=headers,
        json={"document_code": "AADHAAR", "name": "Aadhaar card"},
    )
    assert document.status_code == 201
    readiness = await client.get(
        f"/api/v1/documents/readiness/{scheme.id}", headers=headers
    )
    assert readiness.json()["data"]["readiness_percentage"] == 50.0
    assert readiness.json()["data"]["missing_documents"] == ["Income certificate"]

    plan = await client.post(
        f"/api/v1/action-plans/generate/{scheme.id}", headers=headers
    )
    assert plan.status_code == 200
    assert plan.json()["data"]["plan"]["this_week"][0]["type"] == "document"

    refreshed = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refreshed.status_code == 200
    reused = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reused.status_code == 401
    assert reused.json()["errors"][0]["code"] == "authentication_failed"


@pytest.mark.asyncio
async def test_validation_and_route_protection(client):
    invalid = await client.post(
        "/api/v1/auth/register",
        json={"email": "bad", "password": "weak", "name": "A"},
    )
    assert invalid.status_code == 422
    assert invalid.json()["trace_id"]
    protected = await client.get("/api/v1/profiles/me")
    assert protected.status_code == 401

