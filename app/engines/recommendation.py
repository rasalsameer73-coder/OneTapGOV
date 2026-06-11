from decimal import Decimal

from app.models.enums import DecisionStatus


class RecommendationEngine:
    def score(
        self,
        *,
        eligibility_result,
        profile_completion: int,
        readiness_percentage: float,
        scheme_priority: int,
    ) -> dict:
        all_rules = (
            eligibility_result.eligible_because + eligibility_result.not_eligible_because
        )
        passed = len(eligibility_result.eligible_because)
        match_score = (passed / len(all_rules) * 100) if all_rules else 0
        if eligibility_result.status == DecisionStatus.ELIGIBLE:
            match_score = max(match_score, 90)
        confidence = min(100.0, profile_completion * 0.7 + min(len(all_rules) * 5, 30))
        priority_bonus = max(0.0, 1000 - scheme_priority) / 100
        eligibility_bonus = 20 if eligibility_result.status == DecisionStatus.ELIGIBLE else 0
        priority_score = (
            match_score * 0.5
            + confidence * 0.25
            + readiness_percentage * 0.25
            + priority_bonus
            + eligibility_bonus
        )
        return {
            "match_score": Decimal(str(round(match_score, 2))),
            "confidence_score": Decimal(str(round(confidence, 2))),
            "priority_score": Decimal(str(round(priority_score, 2))),
        }

