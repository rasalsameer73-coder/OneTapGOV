from pydantic import BaseModel
from typing import Optional

class StudentProfile(BaseModel):
    user_id: str
    institution_details: Optional[str] = None
    academic_performance: Optional[str] = None
    minority_status: Optional[str] = None
    disability: Optional[str] = None
    hostel_status: Optional[str] = None
    course_type: Optional[str] = None
    scholarship_purpose: Optional[str] = None
    special_groups: Optional[str] = None
    nationality: Optional[str] = None
    existing_benefits: Optional[str] = None
