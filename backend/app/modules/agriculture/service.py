from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.agriculture.models import AgricultureProfile
from app.modules.agriculture.repository import (
    AgricultureRepository,
)
from app.modules.agriculture.schemas import (
    AgricultureProfileCreate,
    AgricultureProfileUpdate,
)


class AgricultureService:

    def __init__(
        self,
        repository: AgricultureRepository,
    ):
        self.repository = repository

    async def create_agriculture_profile(
        self,
        current_user: User,
        profile_data: AgricultureProfileCreate,
    ) -> AgricultureProfile:

        existing_profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agriculture profile already exists",
            )

        profile = AgricultureProfile(
            user_id=current_user.id,
            land_area_acres=profile_data.land_area_acres,
            land_ownership=profile_data.land_ownership,
            crop_type=profile_data.crop_type,
            pm_kisan_status=profile_data.pm_kisan_status,
            irrigation_available=profile_data.irrigation_available,
            farmer_category=profile_data.farmer_category,
            livestock_owned=profile_data.livestock_owned,
        )

        return await self.repository.create_profile(
            profile
        )

    async def get_agriculture_profile(
        self,
        current_user: User,
    ) -> AgricultureProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agriculture profile not found",
            )

        return profile

    async def update_agriculture_profile(
        self,
        current_user: User,
        profile_data: AgricultureProfileUpdate,
    ) -> AgricultureProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agriculture profile not found",
            )

        profile.land_area_acres = profile_data.land_area_acres
        profile.land_ownership = profile_data.land_ownership
        profile.crop_type = profile_data.crop_type
        profile.pm_kisan_status = profile_data.pm_kisan_status
        profile.irrigation_available = profile_data.irrigation_available
        profile.farmer_category = profile_data.farmer_category
        profile.livestock_owned = profile_data.livestock_owned

        return await self.repository.update_profile(
            profile
        )