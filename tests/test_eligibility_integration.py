from datetime import date
from uuid import uuid4

import pytest

from app.models.schemes import Scheme, SchemeVersion, EligibilityRule, RuleVersion
from app.models.identity import User, Profile
from app.services.eligibility import EligibilityService


@pytest.mark.asyncio
async def test_eligibility_integration_happy_path(session):
    # Create a scheme and published version
    scheme = Scheme(code="INT_TEST", category="Test", state="TestState", is_active=True)
    version = SchemeVersion(version_number=1, name="Integration Test", description="desc", authority="gov", is_published=True)
    from app.repositories.schemes import SchemeRepository

    repo = SchemeRepository(session)
    await repo.create_scheme(scheme, version)

    # Add a simple rule: profile.age >= 18
    rule = EligibilityRule(scheme_id=scheme.id, code="AGE", name="Age check", priority=1)
    rule_version = RuleVersion(version_number=1, expression={"condition": {"field": "profile.age", "operator": "gte", "value": 18}}, explanation_pass="OK", explanation_fail="NO")
    await repo.add_rule(rule, rule_version)

    # Create a user and profile with date_of_birth making them 20 years old
    from sqlalchemy import select
    from app.models.identity import Role
    role = await session.scalar(select(Role).where(Role.name == "citizen"))
    user = User(email="intuser@example.com", role_id=role.id if role else 1, is_active=True, is_verified=True)
    session.add(user)
    await session.flush()
    profile = Profile(user_id=user.id, name="Test", date_of_birth=date.today().replace(year=date.today().year - 20))
    session.add(profile)
    await session.flush()

    svc = EligibilityService(session)
    result = await svc.evaluate(user.id, scheme.id)

    assert result.status.name.lower() == "eligible"
    assert result.eligible_because
