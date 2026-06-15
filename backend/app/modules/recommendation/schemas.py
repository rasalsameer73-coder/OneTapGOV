from pydantic import BaseModel


class SchemeRecommendationResponse(BaseModel):

    scheme_id: int

    scheme_name: str

    match_score: float

    priority: str

    reasons: list[str]

    eligibility_conditions: list[str]

    required_documents: list[str]

    readiness_score: int

    next_steps: list[str]