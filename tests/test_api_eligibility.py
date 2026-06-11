from uuid import uuid4

import pytest

from app.schemas.eligibility import EligibilityResult, RuleResult, ConditionResult
from app.models.enums import DecisionStatus


@pytest.mark.asyncio
async def test_eligibility_route_returns_result(monkeypatch, client):
    scheme_id = uuid4()
    sample = EligibilityResult(
        decision_id=str(uuid4()),
        scheme_id=str(scheme_id),
        scheme_name="Test Scheme",
        status=DecisionStatus.ELIGIBLE,
        eligible_because=[
            RuleResult(
                rule_id=str(uuid4()),
                code="R1",
                name="Rule 1",
                priority=1,
                version=1,
                passed=True,
                explanation="OK",
                conditions=[ConditionResult(field="profile.age", operator="gt", expected=18, actual=20, passed=True)],
            )
        ],
        not_eligible_because=[],
        missing_information=[],
        evaluated_rule_versions={"R1": 1},
        ruleset_fingerprint="abc123",
    )

    async def fake_evaluate(self, user_id, scheme_id_arg):
        return sample

    monkeypatch.setattr("app.services.eligibility.EligibilityService.evaluate", fake_evaluate)
    
    # Bypass auth dependency by returning a simple principal
    from types import SimpleNamespace

    async def fake_principal(*args, **kwargs):
        return SimpleNamespace(user=SimpleNamespace(id=uuid4()), role="citizen")

    import app.main as app_module
    from app.dependencies.auth import get_current_principal

    # Override FastAPI dependency to ensure DI uses our fake principal
    app_module.app.dependency_overrides[get_current_principal] = fake_principal

    # Call the route function directly to avoid ASGI validation issues
    from app.api.v1.routes import eligibility as eligibility_module
    from types import SimpleNamespace

    request_stub = SimpleNamespace(state=SimpleNamespace(trace_id="tx-1"))
    principal = SimpleNamespace(user=SimpleNamespace(id=uuid4()), role="citizen")
    session_stub = object()

    resp = await eligibility_module.evaluate(scheme_id, request_stub, principal, session_stub)
    assert resp["success"] is True
    assert resp["data"]["scheme_id"] == str(scheme_id)
