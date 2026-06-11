from sqlalchemy import select

from app.core.security import create_access_token, hash_password
from app.models.identity import Role, User


async def admin_headers(session):
    role = await session.scalar(select(Role).where(Role.name == "admin"))
    user = User(
        email="admin@example.gov",
        password_hash=hash_password("AdminPassword12"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.commit()
    token, _ = create_access_token(user.id, "admin")
    return {"Authorization": f"Bearer {token}"}


async def citizen(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "citizen2@example.com",
            "password": "CitizenPassword12",
            "name": "Meera Joshi",
        },
    )
    tokens = response.json()["data"]["tokens"]
    return response, {"Authorization": f"Bearer {tokens['access_token']}"}, tokens


async def create_admin_scheme(client, headers):
    response = await client.post(
        "/api/v1/admin/schemes",
        headers=headers,
        json={
            "code": "MH_ADMIN_TEST",
            "category": "Education",
            "state": "Maharashtra",
            "priority": 20,
            "name": "Admin Managed Scholarship",
            "description": "A versioned scholarship managed through the administrative API.",
            "authority": "Government of Maharashtra",
            "benefit_summary": "Tuition support",
            "publish": True,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


async def create_rule(client, headers, scheme_id):
    response = await client.post(
        f"/api/v1/admin/schemes/{scheme_id}/rules",
        headers=headers,
        json={
            "code": "STATE_RULE",
            "name": "Maharashtra residency",
            "priority": 10,
            "expression": {
                "condition": {
                    "field": "profile.state",
                    "operator": "eq",
                    "value": "Maharashtra",
                }
            },
            "explanation_pass": "Maharashtra resident",
            "explanation_fail": "Not a Maharashtra resident",
            "change_note": "Initial rule",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


import pytest


@pytest.mark.asyncio
async def test_admin_lifecycle_and_recommendations(client, session):
    admin = await admin_headers(session)
    scheme_id = await create_admin_scheme(client, admin)
    duplicate = await client.post(
        "/api/v1/admin/schemes",
        headers=admin,
        json={
            "code": "MH_ADMIN_TEST",
            "category": "Education",
            "name": "Duplicate",
            "description": "This duplicate request must be rejected.",
            "authority": "Government",
            "publish": False,
        },
    )
    assert duplicate.status_code == 409
    rule_id = await create_rule(client, admin, scheme_id)

    version = await client.post(
        f"/api/v1/admin/rules/{rule_id}/versions",
        headers=admin,
        json={
            "expression": {
                "all": [
                    {
                        "condition": {
                            "field": "profile.state",
                            "operator": "eq",
                            "value": "Maharashtra",
                        }
                    },
                    {
                        "condition": {
                            "field": "profile.annual_income",
                            "operator": "lte",
                            "value": 300000,
                        }
                    },
                ]
            },
            "explanation_pass": "Resident and income qualified",
            "explanation_fail": "Residency or income requirement not met",
            "change_note": "Add income threshold",
        },
    )
    assert version.status_code == 201
    assert version.json()["data"]["version_number"] == 2

    required_document = await client.post(
        f"/api/v1/admin/schemes/{scheme_id}/required-documents",
        headers=admin,
        json={
            "code": "INCOME_CERT",
            "name": "Income certificate",
            "weight": 100,
            "is_mandatory": True,
        },
    )
    assert required_document.status_code == 201

    updated = await client.patch(
        f"/api/v1/admin/schemes/{scheme_id}",
        headers=admin,
        json={
            "name": "Admin Managed Scholarship 2026",
            "benefit_summary": "Expanded tuition support",
            "change_note": "Annual scheme update",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["current_version"] == 2

    disabled = await client.post(f"/api/v1/admin/schemes/{scheme_id}/disable", headers=admin)
    assert disabled.json()["data"]["is_active"] is False
    enabled = await client.post(f"/api/v1/admin/schemes/{scheme_id}/enable", headers=admin)
    assert enabled.json()["data"]["is_active"] is True
    admin_list = await client.get("/api/v1/admin/schemes", headers=admin)
    assert admin_list.status_code == 200

    public_list = await client.get("/api/v1/schemes")
    assert any(item["id"] == scheme_id for item in public_list.json()["data"]["items"])
    detail = await client.get(f"/api/v1/schemes/{scheme_id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["required_documents"][0]["code"] == "INCOME_CERT"

    registration, citizen_headers, tokens = await citizen(client)
    assert registration.status_code == 201
    profile = await client.patch(
        "/api/v1/profiles/me",
        headers=citizen_headers,
        json={
            "profile": {
                "date_of_birth": "1998-01-01",
                "gender": "female",
                "state": "Maharashtra",
                "district": "Nashik",
                "annual_income": 250000,
                "category": "General",
            }
        },
    )
    assert profile.status_code == 200

    generated = await client.post("/api/v1/recommendations/generate", headers=citizen_headers)
    assert generated.status_code == 200
    assert generated.json()["data"][0]["status"] == "eligible"
    listed = await client.get("/api/v1/recommendations", headers=citizen_headers)
    assert listed.status_code == 200
    assert listed.json()["data"]

    queued = await client.post(
        "/api/v1/notifications",
        headers=citizen_headers,
        json={
            "channel": "email",
            "recipient": "citizen2@example.com",
            "template_code": "recommendations_ready",
            "payload": {"count": 1},
        },
    )
    assert queued.status_code == 202
    notifications = await client.get("/api/v1/notifications", headers=citizen_headers)
    assert len(notifications.json()["data"]) == 1

    document = await client.post(
        "/api/v1/documents",
        headers=citizen_headers,
        json={"document_code": "INCOME_CERT", "name": "Income certificate"},
    )
    document_id = document.json()["data"]["id"]
    verified = await client.patch(
        f"/api/v1/admin/users/{registration.json()['data']['user']['id']}/documents/{document_id}",
        headers=admin,
        json={"status": "verified"},
    )
    assert verified.json()["data"]["status"] == "verified"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "citizen2@example.com", "password": "CitizenPassword12"},
    )
    assert login.status_code == 200
    logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": login.json()["data"]["tokens"]["refresh_token"]},
    )
    assert logout.status_code == 200
    conflict = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "citizen2@example.com",
            "password": "CitizenPassword12",
            "name": "Duplicate Citizen",
        },
    )
    assert conflict.status_code == 409

    missing_rule = await client.post(
        "/api/v1/admin/rules/00000000-0000-0000-0000-000000000001/versions",
        headers=admin,
        json={
            "expression": {
                "condition": {
                    "field": "profile.state",
                    "operator": "eq",
                    "value": "Maharashtra",
                }
            },
            "explanation_pass": "Pass",
            "explanation_fail": "Fail",
            "change_note": "Missing rule",
        },
    )
    assert missing_rule.status_code == 404

    audits = await client.get("/api/v1/admin/audit-logs", headers=admin)
    assert audits.status_code == 200
    assert len(audits.json()["data"]) >= 6

    deleted = await client.delete(f"/api/v1/admin/schemes/{scheme_id}", headers=admin)
    assert deleted.status_code == 204
    missing = await client.get(f"/api/v1/schemes/{scheme_id}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_admin_rbac_and_failed_login(client):
    _, headers, _ = await citizen(client)
    forbidden = await client.get("/api/v1/admin/audit-logs", headers=headers)
    assert forbidden.status_code == 403
    failed = await client.post(
        "/api/v1/auth/login",
        json={"email": "citizen2@example.com", "password": "WrongPassword12"},
    )
    assert failed.status_code == 401
