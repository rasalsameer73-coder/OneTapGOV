from config.basic_questions import BASIC_FIELDS
from config.farmer_questions import FARMER_FIELDS
from config.student_questions import STUDENT_FIELDS
from config.women_questions import WOMEN_FIELDS


class ProfileService:

    @staticmethod
    def get_table_name(field_name: str, sector: str = None):
        if field_name in BASIC_FIELDS:
            return "user_basic_info"
        
        # If sector is provided, prefer that sector's table
        if sector:
            sector_table = ProfileService.get_sector_table(sector)
            sector_fields = ProfileService.get_sector_fields(sector)
            if field_name in sector_fields:
                return sector_table

        if field_name in FARMER_FIELDS:
            return "farmer_profile"
        if field_name in STUDENT_FIELDS:
            return "student_profile"
        if field_name in WOMEN_FIELDS:
            return "women_profile"
        return "user_basic_info"

    @staticmethod
    def get_sector_table(sector: str):
        if not sector:
            return None
        sector_lower = sector.lower()
        if "farmer" in sector_lower:
            return "farmer_profile"
        elif "student" in sector_lower:
            return "student_profile"
        elif "women" in sector_lower:
            return "women_profile"
        return None

    @staticmethod
    def find_first_missing(profile: dict, fields=None):
        if fields is None:
            fields = BASIC_FIELDS

        for field in fields:
            value = profile.get(field)
            if value is None:
                return field
            if isinstance(value, str) and value.strip() == "":
                return field
        return None

    @staticmethod
    def get_sector_fields(sector: str):
        if not sector:
            return []
        
        sector_lower = sector.lower()
        if "farmer" in sector_lower:
            return FARMER_FIELDS
        elif "student" in sector_lower:
            return STUDENT_FIELDS
        elif "women" in sector_lower:
            return WOMEN_FIELDS
        return []

    @staticmethod
    def is_basic_profile_complete(profile: dict):
        return ProfileService.find_first_missing(profile, BASIC_FIELDS) is None

    @staticmethod
    def get_progress(profile: dict, fields=None):
        if fields is None:
            fields = BASIC_FIELDS
            
        total = len(fields)
        if total == 0:
            return {"completed": 0, "total": 0, "percentage": 0}

        completed = 0
        for field in fields:
            value = profile.get(field)
            if value is not None:
                if isinstance(value, str):
                    if value.strip() != "":
                        completed += 1
                else:
                    completed += 1

        percentage = int((completed / total) * 100)
        return {
            "completed": completed,
            "total": total,
            "percentage": percentage
        }