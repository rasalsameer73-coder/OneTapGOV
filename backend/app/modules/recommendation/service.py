from app.modules.recommendation.schemas import (
    SchemeRecommendationResponse,
)

from app.modules.documents.repository import (
    DocumentRepository,
)

from app.modules.eligibility.service import (
    EligibilityService,
)

from app.modules.profile.repository import (
    ProfileRepository,
)
from app.modules.education.repository import (
    EducationRepository,
)
from app.modules.women.repository import (
    WomenRepository,
)
from app.modules.agriculture.repository import (
    AgricultureRepository,
)
from app.modules.schemes.repository import (
    SchemeRepository,
)


class RecommendationService:

    def __init__(
        self,
        scheme_repository: SchemeRepository,
        profile_repository: ProfileRepository,
        education_repository: EducationRepository,
        women_repository: WomenRepository,
        agriculture_repository: AgricultureRepository,
        document_repository: DocumentRepository,
    ):
        self.scheme_repository = scheme_repository
        self.document_repository = document_repository

        self.eligibility_service = EligibilityService(
            scheme_repository=scheme_repository,
            profile_repository=profile_repository,
            education_repository=education_repository,
            women_repository=women_repository,
            agriculture_repository=agriculture_repository,
        )

    async def get_recommendations(
        self,
        current_user,
    ) -> list[SchemeRecommendationResponse]:

        recommendations = []

        eligible_schemes = (
            await self.eligibility_service.get_eligible_schemes(
                current_user
            )
        )

        for scheme in eligible_schemes:

            match_score = scheme.match_score

            # Priority
            if match_score >= 90:
                priority = "High"

            elif match_score >= 70:
                priority = "Medium"

            else:
                priority = "Low"

            # Required Documents
            documents = (
                await self.document_repository.get_documents_by_scheme_id(
                    scheme.scheme_id
                )
            )

            required_documents = [
                document.document_name
                for document in documents
            ]

            # Human-readable conditions
            eligibility_conditions = []

            versions = (
                await self.scheme_repository.get_scheme_versions(
                    scheme.scheme_id
                )
            )

            for version in versions:

                rules = (
                    await self.scheme_repository.get_eligibility_rules(
                        version.id
                    )
                )

                for rule in rules:

                    conditions = (
                        await self.scheme_repository.get_rule_conditions(
                            rule.id
                        )
                    )

                    for condition in conditions:

                        if (
                            condition.human_readable_condition
                        ):

                            eligibility_conditions.append(
                                condition.human_readable_condition
                            )

            # Reasons
            reasons = eligibility_conditions.copy()

            # Next Steps
            next_steps = []

            for document in required_documents:

                next_steps.append(
                    f"Upload {document}"
                )

            next_steps.append(
                "Submit application"
            )

            recommendations.append(

                SchemeRecommendationResponse(

                    scheme_id=scheme.scheme_id,

                    scheme_name=scheme.scheme_name,

                    match_score=match_score,

                    priority=priority,

                    reasons=reasons,

                    eligibility_conditions=eligibility_conditions,

                    required_documents=required_documents,

                    # Will later come from Readiness Engine
                    readiness_score=100,

                    next_steps=next_steps,
                )
            )

        return recommendations