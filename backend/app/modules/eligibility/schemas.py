from pydantic import BaseModel


class EligibleSchemeResponse(BaseModel):
    scheme_id: int

    scheme_name: str

    match_score: float