"""Documents models placeholder."""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SchemeDocument(Base):
    __tablename__ = "scheme_documents"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    scheme_id: Mapped[int] = mapped_column(
        ForeignKey("schemes.id")
    )

    document_name: Mapped[str] = mapped_column(
        String(255)
    )

    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )