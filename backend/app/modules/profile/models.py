from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True
    )

    # Basic Information
    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    annual_income: Mapped[int | None] = mapped_column(
        nullable=True
    )

    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Sector Flags
    is_student: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_woman: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_farmer: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_senior_citizen: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_disabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_worker: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # Progress
    profile_completion_percentage: Mapped[int] = mapped_column(
        default=0
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    ) 