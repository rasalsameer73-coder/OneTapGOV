from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        repository = UserRepository(db)
        service = AuthService(repository)

        user = await service.signup(user_data)

        return user

    except Exception as e:
        import traceback

        print("\n========== SIGNUP ERROR ==========\n")
        traceback.print_exc()
        print("\n==================================\n")

        raise e


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = AuthService(repository)

    # OAuth2 uses "username" field
    payload = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    return await service.login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user=Depends(get_current_user),
):
    return current_user