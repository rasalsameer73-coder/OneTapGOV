import pytest
import asyncio
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime, timezone

from app.services.admin import AdminService
from app.core.exceptions import ConflictError, NotFoundError
from app.core import cache


class DummySession:
    def __init__(self):
        self._added = []

    async def commit(self):
        return None

    async def flush(self):
        return None

    async def refresh(self, obj):
        return None

    def add(self, obj):
        self._added.append(obj)


class DummyScheme:
    def __init__(self, id=None):
        self.id = id or uuid4()
        self.is_active = True
        self.deleted_at = None
        self.current_version = 1


@pytest.mark.asyncio
async def test_create_scheme_conflict(monkeypatch):
    session = DummySession()
    svc = AdminService(session)

    async def fake_get_by_code(code):
        return True

    svc.schemes.get_by_code = fake_get_by_code

    with pytest.raises(ConflictError):
        await svc.create_scheme(uuid4(), SimpleNamespace(code="x", category="c", state="s", priority=1, publish=False, name="n", description=None, authority=None, benefit_summary=None, application_url=None, valid_from=None, valid_until=None), "trace", None)


@pytest.mark.asyncio
async def test_create_scheme_success(monkeypatch):
    session = DummySession()
    svc = AdminService(session)

    async def fake_get_by_code(code):
        return None

    async def fake_create_scheme(scheme, version):
        # mimic DB assigning id
        scheme.id = uuid4()
        version.id = uuid4()

    svc.schemes.get_by_code = fake_get_by_code
    svc.schemes.create_scheme = fake_create_scheme
    async def fake_add(*a, **k):
        return None

    svc.operations.add = fake_add

    req = SimpleNamespace(code="code1", category="cat", state="s", priority=5, publish=True, name="Name", description="d", authority="a", benefit_summary="b", application_url=None, valid_from=None, valid_until=None, model_dump=lambda **k: {"code": "code1"})

    scheme = await svc.create_scheme(uuid4(), req, "trace", "1.2.3.4")
    assert scheme is not None
    assert hasattr(scheme, "id")


@pytest.mark.asyncio
async def test_update_scheme_previous_none_raises(monkeypatch):
    session = DummySession()
    svc = AdminService(session)

    dummy = DummyScheme()

    async def fake_get(sid):
        return dummy

    async def fake_get_current_version(scheme):
        return None

    svc.schemes.get = fake_get
    svc.schemes.get_current_version = fake_get_current_version

    req = SimpleNamespace(category=None, state=None, priority=None, name=None, description=None, authority=None, benefit_summary=None, application_url=None, valid_from=None, valid_until=None, publish=None, change_note=None)

    with pytest.raises(NotFoundError):
        await svc.update_scheme(uuid4(), uuid4(), req, "t", None)


@pytest.mark.asyncio
async def test_set_enabled_and_delete(monkeypatch):
    session = DummySession()
    svc = AdminService(session)

    dummy = DummyScheme()

    async def fake_get(sid):
        return dummy

    svc.schemes.get = fake_get
    async def fake_add(*a, **k):
        return None

    svc.operations.add = fake_add

    # set enabled False
    res = await svc.set_enabled(uuid4(), uuid4(), False, "t", None)
    assert res.is_active is False

    # delete sets deleted_at and is_active False
    await svc.delete_scheme(uuid4(), uuid4(), "t", None)
    assert dummy.deleted_at is not None


@pytest.mark.asyncio
async def test_add_rule_and_version_not_found(monkeypatch):
    session = DummySession()
    svc = AdminService(session)

    async def fake_scheme_exists(sid):
        return True

    svc._scheme = lambda sid: asyncio.sleep(0, result=True)
    async def fake_add_rule(rule, version):
        return None

    svc.schemes.add_rule = fake_add_rule

    async def fake_add(*a, **k):
        return None

    svc.operations.add = fake_add

    expr = SimpleNamespace(model_dump=lambda **k: {"op": "true"})
    req = SimpleNamespace(code="r1", name="n", priority=1, expression=expr, explanation_pass=None, explanation_fail=None, change_note=None, model_dump=lambda **k: {"code": "r1"})

    rule = await svc.add_rule(uuid4(), uuid4(), req, "t", None)
    assert rule is not None

    # add_rule_version when rule not found
    async def fake_get_rule(rid):
        return None

    svc.schemes.get_rule = fake_get_rule
    with pytest.raises(NotFoundError):
        await svc.add_rule_version(uuid4(), uuid4(), SimpleNamespace(expression=expr, explanation_pass=None, explanation_fail=None, change_note=None, model_dump=lambda **k: {}), "t", None)
