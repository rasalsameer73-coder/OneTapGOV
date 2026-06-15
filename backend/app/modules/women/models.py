from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WomenProfile(Base):
    __tablename__ = "women_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True
    )

    marital_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    children_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    pregnancy_status: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    widow_status: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    single_mother_status: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    self_help_group_member: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )