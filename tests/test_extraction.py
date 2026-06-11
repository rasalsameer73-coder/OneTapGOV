from decimal import Decimal

import pytest
from sqlalchemy import select

import app.services.extraction as extraction_module
from app.models.identity import Role, User
from app.services.extraction import AIExtractionService, ExtractionProvider
from app.services.extraction import LocalStructuredExtractionProvider


@pytest.mark.asyncio
async def test_local_extractor_only_extracts_facts():
    provider = LocalStructuredExtractionProvider()
    result, usage = await provider.extract(
        "I am an engineering student from Maharashtra with family income ₹1.8 lakh and OBC category."
    )
    assert result == {
        "state": "Maharashtra",
        "income": Decimal("180000.0"),
        "course": "Engineering",
        "is_student": True,
        "category": "OBC",
    }
    assert usage["input_tokens"] > 0
    assert "eligibility" not in result


@pytest.mark.asyncio
async def test_local_extractor_handles_numeric_income():
    result, _ = await LocalStructuredExtractionProvider().extract(
        "My annual income is Rs 240,000 and I live in Gujarat."
    )
    assert result["income"] == Decimal("240000")
    assert result["state"] == "Gujarat"


@pytest.mark.asyncio
async def test_extraction_retries_and_records_failure(session, monkeypatch):
    role = await session.scalar(select(Role).where(Role.name == "citizen"))
    user = User(email="ai-failure@example.com", role_id=role.id, is_active=True)
    session.add(user)
    await session.commit()

    class FailingProvider(ExtractionProvider):
        async def extract(self, text):
            raise RuntimeError("provider unavailable")

    async def no_sleep(_):
        return None

    monkeypatch.setattr(extraction_module.asyncio, "sleep", no_sleep)
    with pytest.raises(RuntimeError, match="failed after retries"):
        await AIExtractionService(session, FailingProvider()).extract(
            user.id, "I am a student from Maharashtra"
        )
