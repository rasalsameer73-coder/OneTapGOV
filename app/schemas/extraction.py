from decimal import Decimal

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=5, max_length=5000)


class ExtractedProfile(BaseModel):
    state: str | None = None
    district: str | None = None
    income: Decimal | None = Field(default=None, ge=0)
    course: str | None = None
    year: int | None = Field(default=None, ge=1, le=12)
    category: str | None = None
    gender: str | None = None
    crop_type: str | None = None
    is_student: bool | None = None


class ExtractionResponse(BaseModel):
    extracted: ExtractedProfile
    confidence: dict[str, float]
    provider: str
    model: str
    request_id: str

