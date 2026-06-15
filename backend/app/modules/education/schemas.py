from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EducationProfileCreate(BaseModel):
    education_level: str
    institution_name: str

    course: str | None = None
    branch: str | None = None

    academic_year: int | None = None
    semester: int | None = None

    board: str | None = None

    percentage: float | None = None
    cgpa: float | None = None

    current_status: str


class EducationProfileUpdate(BaseModel):
    education_level: str
    institution_name: str

    course: str | None = None
    branch: str | None = None

    academic_year: int | None = None
    semester: int | None = None

    board: str | None = None

    percentage: float | None = None
    cgpa: float | None = None

    current_status: str


class EducationProfileResponse(BaseModel):
    id: int
    user_id: UUID

    education_level: str | None
    institution_name: str | None

    course: str | None
    branch: str | None

    academic_year: int | None
    semester: int | None

    board: str | None

    percentage: float | None
    cgpa: float | None

    current_status: str | None

    model_config = ConfigDict(
        from_attributes=True
    )