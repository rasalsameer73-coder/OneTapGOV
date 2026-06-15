from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EducationProfile(Base):
    __tablename__ = "education_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True
    )

    education_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    institution_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    course: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    branch: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    academic_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    semester: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    board: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    cgpa: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    current_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )