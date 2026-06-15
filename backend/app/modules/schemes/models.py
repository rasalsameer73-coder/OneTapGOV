from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    scheme_name: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    scheme_code: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    official_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class SchemeVersion(Base):
    __tablename__ = "scheme_versions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    scheme_id: Mapped[int] = mapped_column(
        ForeignKey("schemes.id"),
        index=True
    )

    version_number: Mapped[int]

    effective_from: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    effective_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    scheme_version_id: Mapped[int] = mapped_column(
        ForeignKey("scheme_versions.id"),
        index=True
    )

    rule_name: Mapped[str] = mapped_column(
        String(255)
    )

    logical_operator: Mapped[str] = mapped_column(
        String(10),
        default="AND"
    )


class RuleCondition(Base):
    __tablename__ = "rule_conditions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    eligibility_rule_id: Mapped[int] = mapped_column(
        ForeignKey("eligibility_rules.id"),
        index=True
    )

    field_name: Mapped[str] = mapped_column(
        String(100)
    )

    comparison_operator: Mapped[str] = mapped_column(
        String(20)
    )

    comparison_value: Mapped[str] = mapped_column(
        String(255)
    )

    human_readable_condition: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )