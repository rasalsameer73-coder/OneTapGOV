import asyncio
from uuid import uuid4

import pytest

from app.models.enums import DecisionStatus


class FakeScheme:
    def __init__(self, id_):
        self.id = id_
        self.is_active = True


class FakeVersion:
    def __init__(self):
        self.version_number = 1
        self.is_published = True
        self.name = "Test Scheme"


class FakeRule:
    def __init__(self, id_, code="R1", name="Rule 1", priority=1):
        self.id = id_
        self.code = code
        self.name = name
        self.priority = priority


class FakeRuleVersion:
    def __init__(self, expr, version_number=1, pass_msg="ok", fail_msg="no"):
        self.version_number = version_number
        self.expression = expr
        self.explanation_pass = pass_msg
        self.explanation_fail = fail_msg


class FakeSchemeRepo:
    def __init__(self, session):
        pass

    async def get(self, scheme_id):
        return FakeScheme(scheme_id)

    async def get_current_version(self, scheme):
        return FakeVersion()

    async def get_rules(self, scheme_id):
        # Single rule that requires profile.age >= 18
        rule = FakeRule(uuid4(), code="AGE_CHECK", name="Age check", priority=1)
        rule_version = FakeRuleVersion({"condition": {"field": "profile.age", "operator": "gte", "value": 18}})
        return [(rule, rule_version)]


class FakeOperationsRepo:
    def __init__(self, session):
        pass

    async def add(self, decision):
        # mimic DB model by attaching an id
        decision.id = uuid4()
        return decision


class FakeProfileService:
    def __init__(self, session):
        pass

    async def facts(self, user_id):
        return ({"profile": {"age": 20}}, None, None)


@pytest.mark.asyncio
async def test_eligibility_service_eligible(monkeypatch):
    # Patch repositories/services used by EligibilityService
    monkeypatch.setattr("app.services.eligibility.SchemeRepository", FakeSchemeRepo)
    monkeypatch.setattr("app.services.eligibility.OperationsRepository", FakeOperationsRepo)
    monkeypatch.setattr("app.services.eligibility.ProfileService", FakeProfileService)

    # Create a dummy session with async commit used by service
    class DummySession:
        async def commit(self):
            pass

    session = DummySession()

    from app.services.eligibility import EligibilityService

    svc = EligibilityService(session)
    user_id = uuid4()
    scheme_id = uuid4()
    result = await svc.evaluate(user_id, scheme_id)

    assert result.status == DecisionStatus.ELIGIBLE
    assert result.eligible_because


@pytest.mark.asyncio
async def test_eligibility_service_insufficient_data(monkeypatch):
    # Modify profile service to return no age
    monkeypatch.setattr("app.services.eligibility.SchemeRepository", FakeSchemeRepo)
    monkeypatch.setattr("app.services.eligibility.OperationsRepository", FakeOperationsRepo)

    class NoAgeProfile(FakeProfileService):
        async def facts(self, user_id):
            return ({"profile": {}}, None, None)

    monkeypatch.setattr("app.services.eligibility.ProfileService", NoAgeProfile)

    class DummySession:
        async def commit(self):
            pass

    session = DummySession()
    from app.services.eligibility import EligibilityService

    svc = EligibilityService(session)
    user_id = uuid4()
    scheme_id = uuid4()
    result = await svc.evaluate(user_id, scheme_id)

    assert result.status == DecisionStatus.INSUFFICIENT_DATA
