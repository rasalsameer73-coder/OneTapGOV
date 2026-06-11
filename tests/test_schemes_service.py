import pytest
from uuid import uuid4

from app.services.schemes import SchemeQueryService
from app.core.exceptions import NotFoundError


class Dummy:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.mark.asyncio
async def test_list_filters_deleted_and_unpublished(monkeypatch):
    svc = SchemeQueryService(None)

    def fake_model_dict(entity, exclude=None):
        data = dict(getattr(entity, "__dict__", {}))
        if exclude:
            for key in list(exclude):
                data.pop(key, None)
        return data

    monkeypatch.setattr("app.services.schemes.model_dict", fake_model_dict)

    scheme1 = Dummy(id=uuid4(), deleted_at=None)
    scheme2 = Dummy(id=uuid4(), deleted_at=None)
    scheme3 = Dummy(id=uuid4(), deleted_at="deleted")

    # scheme1: has published version
    version1 = Dummy(is_published=True)
    # scheme2: has unpublished version
    version2 = Dummy(is_published=False)

    async def fake_list_active(limit, offset):
        return [scheme1, scheme2, scheme3], 3

    async def fake_get_current_version(scheme):
        if scheme is scheme1:
            return version1
        if scheme is scheme2:
            return version2
        return None

    svc.repository.list_active = fake_list_active
    svc.repository.get_current_version = fake_get_current_version

    result = await svc.list(limit=10, offset=0, include_inactive=False)
    assert result["total"] == 3
    items = result["items"]
    # only scheme1 qualifies
    assert len(items) == 1
    assert items[0]["version"]["is_published"] is True


@pytest.mark.asyncio
async def test_detail_not_found_when_missing_or_inactive(monkeypatch):
    svc = SchemeQueryService(None)

    async def fake_get_none(scheme_id):
        return None

    svc.repository.get = fake_get_none

    with pytest.raises(NotFoundError):
        await svc.detail(uuid4())

    # inactive scheme
    inactive = Dummy(id=uuid4(), is_active=False, deleted_at=None)

    async def fake_get_inactive(scheme_id):
        return inactive

    svc.repository.get = fake_get_inactive

    with pytest.raises(NotFoundError):
        await svc.detail(uuid4())


@pytest.mark.asyncio
async def test_detail_not_found_when_no_published_version(monkeypatch):
    svc = SchemeQueryService(None)

    scheme = Dummy(id=uuid4(), is_active=True, deleted_at=None)

    async def fake_get(scheme_id):
        return scheme

    async def fake_get_current_version_none(scheme):
        return None

    svc.repository.get = fake_get
    svc.repository.get_current_version = fake_get_current_version_none

    with pytest.raises(NotFoundError):
        await svc.detail(uuid4())

    # now return unpublished version
    async def fake_get_current_version_unpublished(scheme):
        return Dummy(is_published=False)

    svc.repository.get_current_version = fake_get_current_version_unpublished

    with pytest.raises(NotFoundError):
        await svc.detail(uuid4())


@pytest.mark.asyncio
async def test_detail_returns_version_and_documents(monkeypatch):
    svc = SchemeQueryService(None)

    scheme = Dummy(id=uuid4(), is_active=True, deleted_at=None, name="S1")
    version = Dummy(is_published=True, name="V1")
    doc1 = Dummy(id=uuid4(), name="D1")

    def fake_model_dict(entity, exclude=None):
        data = dict(getattr(entity, "__dict__", {}))
        if exclude:
            for key in list(exclude):
                data.pop(key, None)
        return data

    monkeypatch.setattr("app.services.schemes.model_dict", fake_model_dict)

    async def fake_get(scheme_id):
        return scheme

    async def fake_get_current_version(scheme_arg):
        return version

    async def fake_get_documents(scheme_id):
        return [doc1]

    svc.repository.get = fake_get
    svc.repository.get_current_version = fake_get_current_version
    svc.repository.get_documents = fake_get_documents

    out = await svc.detail(scheme.id)
    assert out["version"]["is_published"] is True
    assert isinstance(out["required_documents"], list)
    assert out["required_documents"][0]["name"] == "D1"
