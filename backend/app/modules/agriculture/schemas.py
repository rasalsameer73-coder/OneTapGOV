from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgricultureProfileCreate(BaseModel):
    land_area_acres: float | None = None
    land_ownership: str | None = None
    crop_type: str | None = None

    pm_kisan_status: bool = False
    irrigation_available: bool = False

    farmer_category: str | None = None

    livestock_owned: bool = False


class AgricultureProfileUpdate(BaseModel):
    land_area_acres: float | None = None
    land_ownership: str | None = None
    crop_type: str | None = None

    pm_kisan_status: bool = False
    irrigation_available: bool = False

    farmer_category: str | None = None

    livestock_owned: bool = False


class AgricultureProfileResponse(BaseModel):
    id: int
    user_id: UUID

    land_area_acres: float | None
    land_ownership: str | None
    crop_type: str | None

    pm_kisan_status: bool
    irrigation_available: bool

    farmer_category: str | None

    livestock_owned: bool

    model_config = ConfigDict(
        from_attributes=True
    )