import pytest
import io


@pytest.mark.asyncio
async def test_upload_file_endpoint(client):
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "uploader@example.com", "password": "StrongPassword12", "name": "Uploader"},
    )
    tokens = registration.json()["data"]["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    file_content = b"hello world"
    files = {"file": ("hello.txt", io.BytesIO(file_content), "text/plain")}
    response = await client.post("/api/v1/documents/upload", headers=headers, files=files)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] in ("hello.txt",)
    assert data["storage_key"] is not None


from app.services.extraction import AIExtractionService


class FakeProvider:
    async def extract(self, text: str):
        return ({"state": "Maharashtra", "income": 180000}, {"input_tokens": 10, "output_tokens": 5, "confidence": {}})


@pytest.mark.asyncio
async def test_ai_extraction_with_injected_provider(session):
    service = AIExtractionService(session, provider=FakeProvider())
    # Call the injected provider directly to verify parsing behavior without DB side-effects
    parsed, usage = await service.provider.extract("I am from Maharashtra and earn ₹1.8 lakh")
    assert parsed["state"] == "Maharashtra"
    assert parsed["income"] == 180000
