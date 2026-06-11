from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import Gender


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    supabase_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), unique=True, index=True
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Admin(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "admins"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    department: Mapped[str | None] = mapped_column(String(160))
    designation: Mapped[str | None] = mapped_column(String(160))


class Profile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(160))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[Gender | None] = mapped_column(String(32))
    state: Mapped[str | None] = mapped_column(String(120), index=True)
    district: Mapped[str | None] = mapped_column(String(120), index=True)
    annual_income: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), index=True)
    category: Mapped[str | None] = mapped_column(String(80), index=True)


class EducationProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "education_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    course: Mapped[str | None] = mapped_column(String(180), index=True)
    year: Mapped[int | None] = mapped_column(Integer)
    marks: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    is_student: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WomenProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "women_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    marital_status: Mapped[str | None] = mapped_column(String(40))
    children_count: Mapped[int | None] = mapped_column(Integer)
    pregnancy_status: Mapped[bool | None] = mapped_column(Boolean)


class AgricultureProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agriculture_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    land_area_acres: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    land_ownership: Mapped[str | None] = mapped_column(String(80))
    crop_type: Mapped[str | None] = mapped_column(String(120), index=True)
    pm_kisan_status: Mapped[bool | None] = mapped_column(Boolean)


class RefreshToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        Index("ix_refresh_tokens_user_active", "user_id", "revoked_at", "expires_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    family_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id"), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(512))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class AIUsageLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_usage_logs"
    __table_args__ = (Index("ix_ai_usage_user_created", "user_id", "created_at"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    request_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)

