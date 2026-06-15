from pydantic import BaseModel


class ReadinessResponse(BaseModel):

    scheme_id: int

    scheme_name: str

    required_documents: list[str]

    uploaded_documents: list[str]

    missing_documents: list[str]

    readiness_score: int

    estimated_completion_days: int

    next_steps: list[str]