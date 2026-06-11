import pytest
from uuid import UUID

from app.models.schemes import Scheme, SchemeVersion


async def seed_scheme(session):
    scheme = Scheme(
        code="MH_SAVE",
        category="Education",
        state="Maharashtra",
        priority=50,
        is_active=True,
        current_version=1,
    )
    session.add(scheme)
    await session.flush()
    session.add(
        SchemeVersion(
            scheme_id=scheme.id,
            version_number=1,
            name="Save Test Scheme",
            description="Test scheme for saved schemes",
            authority="Gov",
            is_published=True,
        )
    )
    await session.commit()
    return scheme


@pytest.mark.asyncio
async def test_saved_schemes_crud(client, session):
    scheme = await seed_scheme(session)

    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "save@example.com", "password": "StrongPassword12", "name": "Saver"},
    )
    assert registration.status_code == 201
    tokens = registration.json()["data"]["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # create saved scheme
    create = await client.post(
        "/api/v1/saved-schemes",
        headers=headers,
        json={"scheme_id": str(scheme.id)},
    )
    assert create.status_code == 201
    data = create.json()["data"]
    assert data["scheme_id"] == str(scheme.id)

    # list saved schemes
    listing = await client.get("/api/v1/saved-schemes", headers=headers)
    assert listing.status_code == 200
    items = listing.json()["data"]
    assert len(items) == 1
    assert items[0]["scheme_id"] == str(scheme.id)

    # delete saved scheme
    delete = await client.delete(f"/api/v1/saved-schemes/{scheme.id}", headers=headers)
    assert delete.status_code == 200

    listing2 = await client.get("/api/v1/saved-schemes", headers=headers)
    assert listing2.status_code == 200
    assert listing2.json()["data"] == []
