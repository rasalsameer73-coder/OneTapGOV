from uuid import uuid4

import pytest

from app.models.schemes import EligibilityRule, RuleVersion, Scheme, SchemeVersion


async def register(client, email):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword12",
            "name": "Test Citizen",
        },
    )
    token = response.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def scheme_with_rule(session, *, active=True, published=True, with_rule=True):
    scheme = Scheme(
        code=f"EDGE_{uuid4().hex[:16].upper()}",
        category="Education",
        priority=100,
        is_active=active,
        current_version=1,
    )
    session.add(scheme)
    await session.flush()
    session.add(
        SchemeVersion(
            scheme_id=scheme.id,
            version_number=1,
            name="Edge Scheme",
            description="Scheme used to test eligibility edge cases.",
            authority="Test Authority",
            is_published=published,
        )
    )
    if with_rule:
        rule = EligibilityRule(
            scheme_id=scheme.id,
            code="INCOME",
            name="Income limit",
            priority=1,
            current_version=1,
        )
        session.add(rule)
        await session.flush()
        session.add(
            RuleVersion(
                rule_id=rule.id,
                version_number=1,
                expression={
                    "condition": {
                        "field": "profile.annual_income",
                        "operator": "lt",
                        "value": 200000,
                    }
                },
                explanation_pass="Income qualified",
                explanation_fail="Income not qualified",
                is_active=True,
            )
        )
    await session.commit()
    return scheme


@pytest.mark.asyncio
async def test_insufficient_not_eligible_and_empty_rules(client, session):
    headers = await register(client, "edge@example.com")
    scheme = await scheme_with_rule(session)

    insufficient = await client.post(
        f"/api/v1/eligibility/evaluate/{scheme.id}", headers=headers
    )
    assert insufficient.json()["data"]["status"] == "insufficient_data"
    assert insufficient.json()["data"]["missing_information"] == [
        "profile.annual_income"
    ]

    profile = await client.patch(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "profile": {"annual_income": 500000},
            "women": {
                "marital_status": "married",
                "children_count": 1,
                "pregnancy_status": False,
            },
            "agriculture": {
                "land_area_acres": 2.5,
                "land_ownership": "owned",
                "crop_type": "Wheat",
                "pm_kisan_status": True,
            },
        },
    )
    assert profile.status_code == 200
    assert profile.json()["data"]["women"]["children_count"] == 1
    assert profile.json()["data"]["agriculture"]["crop_type"] == "Wheat"

    failed = await client.post(
        f"/api/v1/eligibility/evaluate/{scheme.id}", headers=headers
    )
    assert failed.json()["data"]["status"] == "not_eligible"
    assert failed.json()["data"]["not_eligible_because"]

    empty = await scheme_with_rule(session, with_rule=False)
    no_rules = await client.post(
        f"/api/v1/eligibility/evaluate/{empty.id}", headers=headers
    )
    assert no_rules.json()["data"]["status"] == "insufficient_data"

    inactive = await scheme_with_rule(session, active=False)
    inactive_response = await client.post(
        f"/api/v1/eligibility/evaluate/{inactive.id}", headers=headers
    )
    assert inactive_response.status_code == 404

    unpublished = await scheme_with_rule(session, published=False)
    unpublished_response = await client.post(
        f"/api/v1/eligibility/evaluate/{unpublished.id}", headers=headers
    )
    assert unpublished_response.status_code == 404
