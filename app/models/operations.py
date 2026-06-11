from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
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
from app.models.enums import (
    DecisionStatus,
    DocumentStatus,
    NotificationChannel,
    NotificationStatus,
)


class UserDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_documents"
    __table_args__ = (
        Index("ix_user_documents_user_code_status", "user_id", "document_code", "status"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    document_code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[DocumentStatus] = mapped_column(
        String(40), default=DocumentStatus.UPLOADED, nullable=False
    )
    issued_at: Mapped[date | None] = mapped_column(Date)
    expires_at: Mapped[date | None] = mapped_column(Date)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    document_metadata: Mapped[dict | None] = mapped_column("metadata", JSON)
    rejection_reason: Mapped[str | None] = mapped_column(Text)


class EligibilityDecision(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "eligibility_decisions"
    __table_args__ = (
        Index("ix_eligibility_user_scheme_created", "user_id", "scheme_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    scheme_id: Mapped[UUID] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    scheme_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DecisionStatus] = mapped_column(String(40), nullable=False)
    profile_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    explanation: Mapped[dict] = mapped_column(JSON, nullable=False)
    ruleset_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)


class Recommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        UniqueConstraint("user_id", "scheme_id", name="uq_recommendations_user_scheme"),
        Index("ix_recommendations_user_rank", "user_id", "priority_score"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    scheme_id: Mapped[UUID] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    eligibility_decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("eligibility_decisions.id"), nullable=False
    )
    match_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    explanation: Mapped[dict] = mapped_column(JSON, nullable=False)


class SavedScheme(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "saved_schemes"
    __table_args__ = (
        UniqueConstraint("user_id", "scheme_id", name="uq_saved_schemes_user_scheme"),
        Index("ix_saved_schemes_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheme_id: Mapped[UUID] = mapped_column(ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)


class ActionPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "action_plans"
    __table_args__ = (Index("ix_action_plans_user_status", "user_id", "status"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    scheme_id: Mapped[UUID | None] = mapped_column(ForeignKey("schemes.id"))
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    plan: Mapped[dict] = mapped_column(JSON, nullable=False)


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_status", "user_id", "status", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(String(30), nullable=False)
    template_code: Mapped[str] = mapped_column(String(120), nullable=False)
    recipient: Mapped[str] = mapped_column(String(320), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        String(30), default=NotificationStatus.QUEUED, nullable=False
    )
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    error_message: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_actor_created", "actor_user_id", "created_at"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100))
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    trace_id: Mapped[str | None] = mapped_column(String(80), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now().astimezone()
    )


class HelperSheet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "helper_sheets"
    __table_args__ = (Index("ix_helper_sheets_user", "user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheme_id: Mapped[UUID | None] = mapped_column(ForeignKey("schemes.id"))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

