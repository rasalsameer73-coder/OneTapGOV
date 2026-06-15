from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfileCreate(BaseModel):
    date_of_birth: date
    gender: str
    state: str
    district: str
    annual_income: int
    category: str

    is_student: bool = False
    is_woman: bool = False
    is_farmer: bool = False
    is_senior_citizen: bool = False
    is_disabled: bool = False
    is_worker: bool = False


class ProfileUpdate(BaseModel):
    date_of_birth: date
    gender: str
    state: str
    district: str
    annual_income: int
    category: str

    is_student: bool = False
    is_woman: bool = False
    is_farmer: bool = False
    is_senior_citizen: bool = False
    is_disabled: bool = False
    is_worker: bool = False


class ProfileResponse(BaseModel):
    id: int
    user_id: UUID

    date_of_birth: date | None
    gender: str | None
    state: str | None
    district: str | None
    annual_income: int | None
    category: str | None

    is_student: bool
    is_woman: bool
    is_farmer: bool
    is_senior_citizen: bool
    is_disabled: bool
    is_worker: bool

    profile_completion_percentage: int

    model_config = ConfigDict(
        from_attributes=True
    )