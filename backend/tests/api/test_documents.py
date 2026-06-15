import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_create_document_valid_scheme():
    with TestClient(app) as client:
        payload = {"scheme_id": 1, "document_name": "Unit Test Doc", "is_mandatory": True}
        resp = client.post("/api/v1/documents", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert int(data["scheme_id"]) == 1


def test_create_document_invalid_scheme():
    with TestClient(app) as client:
        payload = {"scheme_id": 0, "document_name": "Bad Doc", "is_mandatory": True}
        resp = client.post("/api/v1/documents", json=payload)
        assert resp.status_code == 400
        assert resp.json()["detail"] == "scheme_id does not exist"
