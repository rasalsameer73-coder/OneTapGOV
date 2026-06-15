from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None
    errors: list[str] | None = None
    trace_id: str | None = None