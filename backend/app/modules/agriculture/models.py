from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgricultureProfile(Base):
    __tablename__ = "agriculture_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True
    )

    land_area_acres: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    land_ownership: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    crop_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pm_kisan_status: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    irrigation_available: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    farmer_category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    livestock_owned: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )