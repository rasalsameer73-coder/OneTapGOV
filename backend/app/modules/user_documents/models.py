from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class UserDocument(Base):
    __tablename__ = "user_documents"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    from uuid import UUID

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True
    )

    document_name: Mapped[str] = mapped_column(
        String(255)
    )

    file_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )