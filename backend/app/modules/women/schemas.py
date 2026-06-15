from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WomenProfileCreate(BaseModel):
    marital_status: str | None = None
    children_count: int | None = None
    pregnancy_status: bool = False
    widow_status: bool = False
    single_mother_status: bool = False
    self_help_group_member: bool = False


class WomenProfileUpdate(BaseModel):
    marital_status: str |None = None
    children_count: int | None = None
    pregnancy_status: bool = False
    widow_status: bool = False
    single_mother_status: bool = False
    self_help_group_member: bool = False


class WomenProfileResponse(BaseModel):
    id: int
    user_id: UUID

    marital_status: str | None
    children_count: int | None

    pregnancy_status: bool
    widow_status: bool
    single_mother_status: bool
    self_help_group_member: bool

    model_config = ConfigDict(
        from_attributes=True
    )