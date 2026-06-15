from app.modules.auth.models import User
from app.modules.profile.models import Profile
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileUpdate,
)


class ProfileService:

    def __init__(
        self,
        repository: ProfileRepository,
    ):
        self.repository = repository

    def calculate_completion_percentage(
        self,
        profile: Profile,
    ) -> int:

        fields = [
            profile.date_of_birth,
            profile.gender,
            profile.state,
            profile.district,
            profile.annual_income,
            profile.category,
        ]

        filled = sum(
            1
            for field in fields
            if field is not None
        )

        return int(
            (filled / len(fields)) * 100
        )

    async def create_profile(
        self,
        current_user: User,
        profile_data: ProfileCreate,
    ) -> Profile:

        existing_profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if existing_profile:
            raise ValueError(
                "Profile already exists"
            )

        profile = Profile(
            user_id=current_user.id,

            date_of_birth=profile_data.date_of_birth,
            gender=profile_data.gender,
            state=profile_data.state,
            district=profile_data.district,
            annual_income=profile_data.annual_income,
            category=profile_data.category,

            is_student=profile_data.is_student,
            is_woman=profile_data.is_woman,
            is_farmer=profile_data.is_farmer,
            is_senior_citizen=profile_data.is_senior_citizen,
            is_disabled=profile_data.is_disabled,
            is_worker=profile_data.is_worker,
        )

        profile.profile_completion_percentage = (
            self.calculate_completion_percentage(
                profile
            )
        )

        return await self.repository.create_profile(
            profile
        )

    async def get_profile(
        self,
        current_user: User,
    ) -> Profile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Profile not found"
            )

        return profile

    async def update_profile(
        self,
        current_user: User,
        profile_data: ProfileUpdate,
    ) -> Profile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Profile not found"
            )

        profile.date_of_birth = (
            profile_data.date_of_birth
        )

        profile.gender = profile_data.gender
        profile.state = profile_data.state
        profile.district = profile_data.district
        profile.annual_income = (
            profile_data.annual_income
        )
        profile.category = profile_data.category

        profile.is_student = profile_data.is_student
        profile.is_woman = profile_data.is_woman
        profile.is_farmer = profile_data.is_farmer
        profile.is_senior_citizen = (
            profile_data.is_senior_citizen
        )
        profile.is_disabled = (
            profile_data.is_disabled
        )
        profile.is_worker = profile_data.is_worker

        profile.profile_completion_percentage = (
            self.calculate_completion_percentage(
                profile
            )
        )

        return await self.repository.update_profile(
            profile
        )