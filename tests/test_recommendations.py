import asyncio
from types import SimpleNamespace
from uuid import uuid4, UUID

import pytest

from app.services.recommendations import RecommendationService
from app.core import cache as core_cache


class DummyRule:
    def __init__(self, code="R1"):
        self.code = code

    def model_dump(self, mode="json"):
        return {"code": self.code}


class DummyEligibilityResult:
    def __init__(self, decision_id=None, status="ELIGIBLE"):
        self.decision_id = decision_id or str(uuid4())
        self.status = status
        self.eligible_because = [DummyRule()]
        self.not_eligible_because = []


@pytest.mark.asyncio
async def test_generate_creates_and_returns_recommendations(monkeypatch):
    user_id = uuid4()

    # Create service with a dummy session
    class DummySession:
        async def commit(self):
            pass

    service = RecommendationService(session=DummySession())

    # Fake scheme
    scheme_id = uuid4()
    scheme = SimpleNamespace(id=scheme_id, priority=1, is_active=True)

    async def fake_list_active(limit=1000):
        return [scheme], 1

    async def fake_get_profile(uid):
        return {"completion_percentage": 0.42}

    async def fake_evaluate(uid, sid):
        return DummyEligibilityResult()

    async def fake_readiness(uid, sid):
        return {"readiness_percentage": 0.13}

    def fake_score(**kwargs):
        return {"match_score": 0.5, "confidence_score": 0.6, "priority_score": 0.7}

    captured = {}

    async def fake_replace_recommendations(uid, rows):
        captured["rows"] = rows

    # Patch dependencies on the service instance
    service.schemes = SimpleNamespace(list_active=fake_list_active)
    service.profiles = SimpleNamespace(get=fake_get_profile)
    service.eligibility = SimpleNamespace(evaluate=fake_evaluate)
    service.documents = SimpleNamespace(readiness=fake_readiness)
    service.engine = SimpleNamespace(score=fake_score)
    service.operations = SimpleNamespace(replace_recommendations=fake_replace_recommendations)

    # Run generate
    generated = await service.generate(user_id)

    assert isinstance(generated, list)
    assert len(generated) == 1
    item = generated[0]
    assert item["scheme_id"] == str(scheme_id)
    assert item["match_score"] == pytest.approx(0.5)
    assert item["priority_score"] == pytest.approx(0.7)
    assert "explanation" in item
    # Ensure replace_recommendations received Recommendation rows
    assert "rows" in captured
    assert len(captured["rows"]) == 1


@pytest.mark.asyncio
async def test_list_uses_cache(monkeypatch):
    user_id = uuid4()
    class DummySession:
        pass

    service = RecommendationService(session=DummySession())

    cached_value = [
        {
            "id": "1",
            "scheme_id": "2",
            "match_score": 0.1,
            "confidence_score": 0.2,
            "priority_score": 0.3,
            "explanation": {},
        }
    ]

    async def fake_get_json(key):
        return cached_value

    monkeypatch.setattr(core_cache, "get_json", fake_get_json)

    result = await service.list(user_id)
    assert result == cached_value
