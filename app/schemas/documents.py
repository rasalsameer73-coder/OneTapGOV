from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import DocumentStatus


class UserDocumentCreate(BaseModel):
    document_code: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    storage_key: str | None = Field(default=None, max_length=1000)
    issued_at: date | None = None
    expires_at: date | None = None
    metadata: dict[str, Any] | None = None


class DocumentStatusUpdate(BaseModel):
    status: DocumentStatus
    rejection_reason: str | None = Field(default=None, max_length=2000)


class ReadinessBreakdown(BaseModel):
    code: str
    name: str
    weight: float
    available: bool
    status: str | None


class ReadinessResult(BaseModel):
    scheme_id: str
    readiness_percentage: float
    earned_weight: float
    total_weight: float
    breakdown: list[ReadinessBreakdown]
    missing_documents: list[str]

