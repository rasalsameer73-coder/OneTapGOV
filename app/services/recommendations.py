from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache as core_cache
from app.engines.recommendation import RecommendationEngine
from app.models.operations import Recommendation
from app.repositories.operations import OperationsRepository
from app.repositories.schemes import SchemeRepository
from app.services.documents import DocumentService
from app.services.eligibility import EligibilityService
from app.services.profiles import ProfileService


class RecommendationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schemes = SchemeRepository(session)
        self.operations = OperationsRepository(session)
        self.profiles = ProfileService(session)
        self.eligibility = EligibilityService(session)
        self.documents = DocumentService(session)
        self.engine = RecommendationEngine()

    async def generate(self, user_id: UUID) -> list[dict]:
        schemes, _ = await self.schemes.list_active(limit=1000)
        profile = await self.profiles.get(user_id)
        generated = []
        rows = []
        for scheme in schemes:
            result = await self.eligibility.evaluate(user_id, scheme.id)
            readiness = await self.documents.readiness(user_id, scheme.id)
            scores = self.engine.score(
                eligibility_result=result,
                profile_completion=profile["completion_percentage"],
                readiness_percentage=readiness["readiness_percentage"],
                scheme_priority=scheme.priority,
            )
            row = Recommendation(
                user_id=user_id,
                scheme_id=scheme.id,
                eligibility_decision_id=UUID(result.decision_id),
                explanation={
                    "eligible_because": [
                        item.model_dump(mode="json") for item in result.eligible_because
                    ],
                    "not_eligible_because": [
                        item.model_dump(mode="json")
                        for item in result.not_eligible_because
                    ],
                    "readiness": readiness,
                },
                **scores,
            )
            rows.append(row)
            generated.append(
                {
                    "scheme_id": str(scheme.id),
                    "status": result.status,
                    **{key: float(value) for key, value in scores.items()},
                    "explanation": row.explanation,
                }
            )
        await self.operations.replace_recommendations(user_id, rows)
        await self.session.commit()
        generated.sort(key=lambda item: item["priority_score"], reverse=True)
        await core_cache.set_json(f"recommendations:{user_id}", generated, ttl_seconds=300)
        return generated

    async def list(self, user_id: UUID) -> list[dict]:
        cached = await core_cache.get_json(f"recommendations:{user_id}")
        if cached is not None:
            return cached
        rows = await self.operations.list_recommendations(user_id)
        return [
            {
                "id": str(row.id),
                "scheme_id": str(row.scheme_id),
                "match_score": float(row.match_score),
                "confidence_score": float(row.confidence_score),
                "priority_score": float(row.priority_score),
                "explanation": row.explanation,
            }
            for row in rows
        ]

