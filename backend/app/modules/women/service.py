from app.modules.auth.models import User
from app.modules.women.models import WomenProfile
from app.modules.women.repository import WomenRepository
from app.modules.women.schemas import (
    WomenProfileCreate,
    WomenProfileUpdate,
)


class WomenService:

    def __init__(
        self,
        repository: WomenRepository,
    ):
        self.repository = repository

    async def create_women_profile(
        self,
        current_user: User,
        profile_data: WomenProfileCreate,
    ) -> WomenProfile:

        existing_profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if existing_profile:
            raise ValueError(
                "Women profile already exists"
            )

        profile = WomenProfile(
            user_id=current_user.id,
            marital_status=profile_data.marital_status,
            children_count=profile_data.children_count,
            pregnancy_status=profile_data.pregnancy_status,
            widow_status=profile_data.widow_status,
            single_mother_status=profile_data.single_mother_status,
            self_help_group_member=profile_data.self_help_group_member,
        )

        return await self.repository.create_profile(
            profile
        )

    async def get_women_profile(
        self,
        current_user: User,
    ) -> WomenProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Women profile not found"
            )

        return profile

    async def update_women_profile(
        self,
        current_user: User,
        profile_data: WomenProfileUpdate,
    ) -> WomenProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Women profile not found"
            )

        profile.marital_status = profile_data.marital_status
        profile.children_count = profile_data.children_count
        profile.pregnancy_status = profile_data.pregnancy_status
        profile.widow_status = profile_data.widow_status
        profile.single_mother_status = (
            profile_data.single_mother_status
        )
        profile.self_help_group_member = (
            profile_data.self_help_group_member
        )

        return await self.repository.update_profile(
            profile
        )