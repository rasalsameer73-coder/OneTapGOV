from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.women.repository import WomenRepository
from app.modules.women.schemas import (
    WomenProfileCreate,
    WomenProfileUpdate,
    WomenProfileResponse,
)
from app.modules.women.service import WomenService


router = APIRouter()


@router.post(
    "",
    response_model=WomenProfileResponse,
)
async def create_women_profile(
    profile_data: WomenProfileCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WomenRepository(db)

    service = WomenService(repository)

    return await service.create_women_profile(
        current_user,
        profile_data,
    )


@router.get(
    "",
    response_model=WomenProfileResponse,
)
async def get_women_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WomenRepository(db)

    service = WomenService(repository)

    return await service.get_women_profile(
        current_user
    )


@router.put(
    "",
    response_model=WomenProfileResponse,
)
async def update_women_profile(
    profile_data: WomenProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WomenRepository(db)

    service = WomenService(repository)

    return await service.update_women_profile(
        current_user,
        profile_data,
    )