import pytest


@pytest.mark.asyncio
async def test_helper_sheet_crud(client):
    # register and get tokens
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "helper@example.com", "password": "StrongPassword12", "name": "Helper"},
    )
    assert registration.status_code == 201
    tokens = registration.json()["data"]["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # create
    create = await client.post(
        "/api/v1/helper-sheets",
        headers=headers,
        json={"title": "My Helper", "data": {"name": "A"}},
    )
    assert create.status_code == 201
    sheet = create.json()["data"]
    assert sheet["title"] == "My Helper"

    # list
    listing = await client.get("/api/v1/helper-sheets", headers=headers)
    assert listing.status_code == 200
    items = listing.json()["data"]
    assert len(items) == 1

    # get
    get = await client.get(f"/api/v1/helper-sheets/{sheet['id']}", headers=headers)
    assert get.status_code == 200
    assert get.json()["data"]["title"] == "My Helper"

    # delete
    delete = await client.delete(f"/api/v1/helper-sheets/{sheet['id']}", headers=headers)
    assert delete.status_code == 200
    listing2 = await client.get("/api/v1/helper-sheets", headers=headers)
    assert listing2.json()["data"] == []
