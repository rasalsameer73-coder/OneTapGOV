from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import NotificationChannel


class NotificationCreate(BaseModel):
    channel: NotificationChannel
    recipient: str = Field(min_length=3, max_length=320)
    template_code: str = Field(min_length=2, max_length=120)
    payload: dict[str, Any]

