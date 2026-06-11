import asyncio
from uuid import uuid4, UUID

import pytest

from app.services.recommendations import RecommendationService
from app.core.cache import cache


class Dummy:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class DummyResult:
    def __init__(self, decision_id, status, eligible=None, not_eligible=None):
        self.decision_id = decision_id
        self.status = status
        self.eligible_because = eligible or []
        self.not_eligible_because = not_eligible or []


class Item:
    def __init__(self, payload):
        self._payload = payload

    def model_dump(self, mode=None):
        return self._payload


@pytest.mark.asyncio
async def test_generate_creates_and_caches_recommendations(monkeypatch):
    user_id = uuid4()

    # create service with a dummy session
    class Session:
        async def commit(self):
            pass

    session = Session()
    svc = RecommendationService(session)

    scheme_id = uuid4()
    scheme = Dummy(id=scheme_id, priority=5)

    async def fake_list_active(limit=1000):
        return [scheme], None

    async def fake_get(user_id_arg):
        return {"completion_percentage": 42.0}

    async def fake_evaluate(user_id_arg, scheme_id_arg):
        return DummyResult(str(uuid4()), "eligible", eligible=[Item({"k": 1})], not_eligible=[Item({"m": 2})])

    async def fake_readiness(user_id_arg, scheme_id_arg):
        return {"readiness_percentage": 10.0}

    def fake_score(eligibility_result, profile_completion, readiness_percentage, scheme_priority):
        return {"match_score": 0.5, "confidence_score": 0.6, "priority_score": 1.2}

    captured = {}

    async def fake_replace_recommendations(user_id_arg, rows):
        captured["rows"] = rows

    # monkeypatch internals
    svc.schemes.list_active = fake_list_active
    svc.profiles.get = fake_get
    svc.eligibility.evaluate = fake_evaluate
    svc.documents.readiness = fake_readiness
    svc.engine.score = fake_score
    svc.operations.replace_recommendations = fake_replace_recommendations

    async_calls = {"cache_set": False}

    async def fake_cache_set(key, value, ttl_seconds=0):
        async_calls["cache_set"] = True
        async_calls["cached_value"] = value

    monkeypatch.setattr(cache, "set_json", fake_cache_set)

    generated = await svc.generate(user_id)

    assert isinstance(generated, list)
    assert len(generated) == 1
    assert async_calls["cache_set"] is True
    assert captured.get("rows") is not None
    # ensure fields present
    item = generated[0]
    assert "scheme_id" in item and "priority_score" in item


@pytest.mark.asyncio
async def test_list_uses_cache_and_falls_back(monkeypatch):
    user_id = uuid4()
    svc = RecommendationService(None)

    # case 1: cache hit
    cached = [{"scheme_id": str(uuid4()), "priority_score": 1.0}]

    async def fake_get_json(key):
        return cached

    monkeypatch.setattr(cache, "get_json", fake_get_json)

    got = await svc.list(user_id)
    assert got == cached

    # case 2: cache miss -> operations.list_recommendations
    async def fake_get_json_none(key):
        return None

    class Row:
        def __init__(self):
            self.id = uuid4()
            self.scheme_id = uuid4()
            self.match_score = 0.1
            self.confidence_score = 0.2
            self.priority_score = 0.3
            self.explanation = {"x": 1}

    async def fake_list_recommendations(user_id_arg):
        return [Row()]

    monkeypatch.setattr(cache, "get_json", fake_get_json_none)
    svc.operations.list_recommendations = fake_list_recommendations

    got2 = await svc.list(user_id)
    assert isinstance(got2, list)
    assert len(got2) == 1
    row = got2[0]
    assert "id" in row and "scheme_id" in row and "match_score" in row
