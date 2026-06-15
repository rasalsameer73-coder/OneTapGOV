from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str | None = None
    preferred_language: str = "en"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    phone_number: str | None
    preferred_language: str
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"