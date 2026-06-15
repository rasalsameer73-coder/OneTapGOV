from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserDocumentCreate(BaseModel):

    document_name: str

    file_url: str | None = None


class UserDocumentResponse(BaseModel):

    id: int

    user_id: UUID

    document_name: str

    file_url: str | None

    is_verified: bool

    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )