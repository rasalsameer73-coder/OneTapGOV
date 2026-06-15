from app.modules.auth.models import User
from app.modules.education.models import EducationProfile
from app.modules.education.repository import (
    EducationRepository,
)
from app.modules.education.schemas import (
    EducationProfileCreate,
    EducationProfileUpdate,
)


class EducationService:

    def __init__(
        self,
        repository: EducationRepository,
    ):
        self.repository = repository

    async def create_education_profile(
        self,
        current_user: User,
        profile_data: EducationProfileCreate,
    ) -> EducationProfile:

        existing_profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if existing_profile:
            raise ValueError(
                "Education profile already exists"
            )

        profile = EducationProfile(
            user_id=current_user.id,
            education_level=profile_data.education_level,
            institution_name=profile_data.institution_name,
            course=profile_data.course,
            branch=profile_data.branch,
            academic_year=profile_data.academic_year,
            semester=profile_data.semester,
            board=profile_data.board,
            percentage=profile_data.percentage,
            cgpa=profile_data.cgpa,
            current_status=profile_data.current_status,
        )

        return await self.repository.create_profile(
            profile
        )

    async def get_education_profile(
        self,
        current_user: User,
    ) -> EducationProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Education profile not found"
            )

        return profile

    async def update_education_profile(
        self,
        current_user: User,
        profile_data: EducationProfileUpdate,
    ) -> EducationProfile:

        profile = (
            await self.repository.get_by_user_id(
                current_user.id
            )
        )

        if not profile:
            raise ValueError(
                "Education profile not found"
            )

        profile.education_level = profile_data.education_level
        profile.institution_name = profile_data.institution_name
        profile.course = profile_data.course
        profile.branch = profile_data.branch
        profile.academic_year = profile_data.academic_year
        profile.semester = profile_data.semester
        profile.board = profile_data.board
        profile.percentage = profile_data.percentage
        profile.cgpa = profile_data.cgpa
        profile.current_status = profile_data.current_status

        return await self.repository.update_profile(
            profile
        )