from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.enums import Gender


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    date_of_birth: date | None = None
    gender: Gender | None = None
    state: str | None = Field(default=None, max_length=120)
    district: str | None = Field(default=None, max_length=120)
    annual_income: Decimal | None = Field(default=None, ge=0, le=1_000_000_000)
    category: str | None = Field(default=None, max_length=80)

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_not_future(cls, value: date | None) -> date | None:
        if value and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class EducationProfileUpdate(BaseModel):
    course: str | None = Field(default=None, max_length=180)
    year: int | None = Field(default=None, ge=1, le=12)
    marks: Decimal | None = Field(default=None, ge=0, le=100)
    is_student: bool | None = None


class WomenProfileUpdate(BaseModel):
    marital_status: str | None = Field(default=None, max_length=40)
    children_count: int | None = Field(default=None, ge=0, le=30)
    pregnancy_status: bool | None = None


class AgricultureProfileUpdate(BaseModel):
    land_area_acres: Decimal | None = Field(default=None, ge=0, le=1_000_000)
    land_ownership: str | None = Field(default=None, max_length=80)
    crop_type: str | None = Field(default=None, max_length=120)
    pm_kisan_status: bool | None = None


class CompleteProfileUpdate(BaseModel):
    profile: ProfileUpdate | None = None
    education: EducationProfileUpdate | None = None
    women: WomenProfileUpdate | None = None
    agriculture: AgricultureProfileUpdate | None = None


class ProfileResponse(BaseModel):
    profile: dict
    education: dict | None
    women: dict | None
    agriculture: dict | None
    completion_percentage: int
    missing_fields: list[str]

