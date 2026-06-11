from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    field: str | None = None
    detail: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[ErrorDetail] = Field(default_factory=list)
    trace_id: str


class Pagination(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


def success_response(
    *,
    data: Any,
    message: str,
    trace_id: str,
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": [],
        "trace_id": trace_id,
    }

