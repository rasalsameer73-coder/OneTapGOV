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
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Scheme(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "schemes"
    __table_args__ = (
        Index("ix_schemes_active_category", "is_active", "category"),
        Index("ix_schemes_active_state", "is_active", "state"),
    )

    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str | None] = mapped_column(String(120), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SchemeVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheme_versions"
    __table_args__ = (
        UniqueConstraint("scheme_id", "version_number", name="uq_scheme_versions_number"),
        Index("ix_scheme_versions_published", "scheme_id", "is_published"),
    )

    scheme_id: Mapped[UUID] = mapped_column(
        ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    authority: Mapped[str] = mapped_column(String(200), nullable=False)
    benefit_summary: Mapped[str | None] = mapped_column(Text)
    application_url: Mapped[str | None] = mapped_column(String(1000))
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    change_note: Mapped[str | None] = mapped_column(Text)


class EligibilityRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "eligibility_rules"
    __table_args__ = (
        UniqueConstraint("scheme_id", "code", name="uq_eligibility_rules_code"),
        Index("ix_rules_scheme_active_priority", "scheme_id", "is_active", "priority"),
    )

    scheme_id: Mapped[UUID] = mapped_column(
        ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class RuleVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "rule_versions"
    __table_args__ = (
        UniqueConstraint("rule_id", "version_number", name="uq_rule_versions_number"),
        Index("ix_rule_versions_active", "rule_id", "is_active"),
    )

    rule_id: Mapped[UUID] = mapped_column(
        ForeignKey("eligibility_rules.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    expression: Mapped[dict] = mapped_column(JSON, nullable=False)
    explanation_pass: Mapped[str] = mapped_column(String(500), nullable=False)
    explanation_fail: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    change_note: Mapped[str | None] = mapped_column(Text)


class RequiredDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "required_documents"
    __table_args__ = (
        UniqueConstraint("scheme_id", "code", name="uq_required_documents_code"),
        Index("ix_required_documents_scheme", "scheme_id", "is_active"),
    )

    scheme_id: Mapped[UUID] = mapped_column(
        ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_schema: Mapped[dict | None] = mapped_column(JSON)
