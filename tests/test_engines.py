from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.engines.action_plan import ActionPlanEngine
from app.engines.readiness import ReadinessEngine
from app.engines.recommendation import RecommendationEngine
from app.models.enums import DecisionStatus, DocumentStatus


def test_readiness_weighted_breakdown():
    now = datetime.now(UTC)
    requirements = [
        SimpleNamespace(code="AADHAAR", name="Aadhaar", weight=Decimal("25"), is_mandatory=True),
        SimpleNamespace(code="INCOME", name="Income certificate", weight=Decimal("25"), is_mandatory=True),
        SimpleNamespace(code="PHOTO", name="Photo", weight=Decimal("10"), is_mandatory=False),
    ]
    documents = [
        SimpleNamespace(
            document_code="AADHAAR",
            status=DocumentStatus.VERIFIED,
            updated_at=now,
        ),
        SimpleNamespace(
            document_code="INCOME",
            status=DocumentStatus.REJECTED,
            updated_at=now,
        ),
        SimpleNamespace(
            document_code="AADHAAR",
            status=DocumentStatus.REJECTED,
            updated_at=now - timedelta(days=1),
        ),
    ]
    result = ReadinessEngine().calculate(requirements, documents)
    assert result["readiness_percentage"] == 41.67
    assert result["missing_documents"] == ["Income certificate"]
    assert result["breakdown"][0]["available"] is True


def test_readiness_with_no_requirements_is_complete():
    assert ReadinessEngine().calculate([], [])["readiness_percentage"] == 100.0


def test_action_plan_for_eligible_and_incomplete_users():
    engine = ActionPlanEngine()
    eligible = engine.build(
        missing_documents=["Income certificate"],
        missing_information=["profile.district"],
        eligibility_status="eligible",
        scheme_name="Scholarship",
    )
    assert eligible["today"][0]["type"] == "profile"
    assert eligible["this_week"][0]["type"] == "document"
    assert "Scholarship" in eligible["next_steps"][0]["title"]
    incomplete = engine.build(
        missing_documents=[],
        missing_information=[],
        eligibility_status="insufficient_data",
        scheme_name="Scholarship",
    )
    assert incomplete["next_steps"][0]["type"] == "recheck"


def test_recommendation_scoring():
    result = SimpleNamespace(
        status=DecisionStatus.ELIGIBLE,
        eligible_because=[1, 2],
        not_eligible_because=[],
    )
    scores = RecommendationEngine().score(
        eligibility_result=result,
        profile_completion=80,
        readiness_percentage=75,
        scheme_priority=10,
    )
    assert scores["match_score"] == Decimal("100.0")
    assert scores["confidence_score"] == Decimal("66.0")
    assert scores["priority_score"] > 100

