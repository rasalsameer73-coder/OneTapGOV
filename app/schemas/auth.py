from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=2, max_length=160)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        checks = (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
        )
        if not all(checks):
            raise ValueError("password must include upper, lower, and numeric characters")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class SupabaseExchangeRequest(BaseModel):
    access_token: str = Field(min_length=32)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserSummary(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_verified: bool
