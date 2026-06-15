from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
)
from app.modules.profile.repository import (
    ProfileRepository,
)
from app.modules.profile.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from app.modules.profile.service import (
    ProfileService,
)

router = APIRouter()


@router.post(
    "",
    response_model=ProfileResponse,
)
async def create_profile(
    profile_data: ProfileCreate,
    current_user=Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = ProfileRepository(db)

    service = ProfileService(
        repository
    )

    return await service.create_profile(
        current_user,
        profile_data,
    )


@router.get(
    "",
    response_model=ProfileResponse,
)
async def get_profile(
    current_user=Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = ProfileRepository(db)

    service = ProfileService(
        repository
    )

    return await service.get_profile(
        current_user
    )


@router.put(
    "",
    response_model=ProfileResponse,
)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user=Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = ProfileRepository(db)

    service = ProfileService(
        repository
    )

    return await service.update_profile(
        current_user,
        profile_data,
    )