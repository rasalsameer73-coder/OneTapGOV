from fastapi import HTTPException, status

from app.core.jwt import create_access_token
from app.core.security import (
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import (
    UserCreate,
    UserLogin,
)


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def signup(
        self,
        user_data: UserCreate,
    ) -> User:

        existing_user = await self.repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        user = User(
            email=user_data.email,
            hashed_password=hash_password(
                user_data.password
            ),
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            preferred_language=user_data.preferred_language,
        )

        return await self.repository.create_user(
            user
        )

    async def login(
        self,
        user_data: UserLogin,
    ):
        user = await self.repository.get_by_email(
            user_data.email
        )

        if (
            not user
            or not verify_password(
                user_data.password,
                user.hashed_password,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token = create_access_token(
            {
                "sub": str(user.id)
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }