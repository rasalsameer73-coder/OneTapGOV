from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.eligibility import RuleExpression


class SchemeCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80, pattern=r"^[A-Z0-9_-]+$")
    category: str = Field(min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=120)
    priority: int = Field(default=100, ge=1, le=10000)
    name: str = Field(min_length=3, max_length=240)
    description: str = Field(min_length=10, max_length=10000)
    authority: str = Field(min_length=2, max_length=200)
    benefit_summary: str | None = Field(default=None, max_length=5000)
    application_url: HttpUrl | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    publish: bool = False


class SchemeUpdate(BaseModel):
    category: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=120)
    priority: int | None = Field(default=None, ge=1, le=10000)
    name: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=10000)
    authority: str | None = Field(default=None, max_length=200)
    benefit_summary: str | None = Field(default=None, max_length=5000)
    application_url: HttpUrl | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    publish: bool | None = None
    change_note: str = Field(default="Administrative update", max_length=1000)


class RuleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=100, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=200)
    priority: int = Field(default=100, ge=1, le=10000)
    expression: RuleExpression
    explanation_pass: str = Field(min_length=2, max_length=500)
    explanation_fail: str = Field(min_length=2, max_length=500)
    change_note: str | None = Field(default=None, max_length=1000)


class RuleVersionCreate(BaseModel):
    expression: RuleExpression
    explanation_pass: str = Field(min_length=2, max_length=500)
    explanation_fail: str = Field(min_length=2, max_length=500)
    change_note: str = Field(min_length=2, max_length=1000)


class RequiredDocumentCreate(BaseModel):
    code: str = Field(min_length=2, max_length=100, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    weight: Decimal = Field(gt=0, le=100)
    is_mandatory: bool = True
    metadata_schema: dict[str, Any] | None = None

