from app.modules.profile.models import Profile
from app.modules.education.models import EducationProfile
from app.modules.women.models import WomenProfile
from app.modules.agriculture.models import AgricultureProfile


class UserContextBuilder:

    @staticmethod
    def build(
        profile: Profile | None,
        education: EducationProfile | None,
        women: WomenProfile | None,
        agriculture: AgricultureProfile | None,
    ) -> dict:

        context = {}

        # Profile fields
        if profile:
            context.update(
                {
                    "date_of_birth": profile.date_of_birth,
                    "gender": profile.gender,
                    "state": profile.state,
                    "district": profile.district,
                    "annual_income": profile.annual_income,
                    "category": profile.category,

                    "is_student": profile.is_student,
                    "is_woman": profile.is_woman,
                    "is_farmer": profile.is_farmer,
                    "is_senior_citizen": profile.is_senior_citizen,
                    "is_disabled": profile.is_disabled,
                    "is_worker": profile.is_worker,
                }
            )

        # Education fields
        if education:
            context.update(
                {
                    "education_level": education.education_level,
                    "institution_name": education.institution_name,
                    "course": education.course,
                    "branch": education.branch,
                    "academic_year": education.academic_year,
                    "semester": education.semester,
                    "board": education.board,
                    "percentage": education.percentage,
                    "cgpa": education.cgpa,
                    "current_status": education.current_status,
                }
            )

        # Women fields
        if women:
            context.update(
                {
                    "marital_status": women.marital_status,
                    "children_count": women.children_count,
                    "pregnancy_status": women.pregnancy_status,
                    "widow_status": women.widow_status,
                    "single_mother_status": women.single_mother_status,
                    "self_help_group_member": women.self_help_group_member,
                }
            )

        # Agriculture fields
        if agriculture:
            context.update(
                {
                    "land_area_acres": agriculture.land_area_acres,
                    "land_ownership": agriculture.land_ownership,
                    "crop_type": agriculture.crop_type,
                    "pm_kisan_status": agriculture.pm_kisan_status,
                    "irrigation_available": agriculture.irrigation_available,
                    "farmer_category": agriculture.farmer_category,
                    "livestock_owned": agriculture.livestock_owned,
                }
            )

        return context