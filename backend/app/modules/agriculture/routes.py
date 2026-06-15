from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.agriculture.repository import AgricultureRepository
from app.modules.agriculture.schemas import (
    AgricultureProfileCreate,
    AgricultureProfileUpdate,
    AgricultureProfileResponse,
)
from app.modules.agriculture.service import AgricultureService


router = APIRouter()


@router.post(
    "",
    response_model=AgricultureProfileResponse,
)
async def create_agriculture_profile(
    profile_data: AgricultureProfileCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = AgricultureRepository(db)

    service = AgricultureService(repository)

    return await service.create_agriculture_profile(
        current_user,
        profile_data,
    )


@router.get(
    "",
    response_model=AgricultureProfileResponse,
)
async def get_agriculture_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = AgricultureRepository(db)

    service = AgricultureService(repository)

    return await service.get_agriculture_profile(
        current_user
    )


@router.put(
    "",
    response_model=AgricultureProfileResponse,
)
async def update_agriculture_profile(
    profile_data: AgricultureProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = AgricultureRepository(db)

    service = AgricultureService(repository)

    return await service.update_agriculture_profile(
        current_user,
        profile_data,
    )