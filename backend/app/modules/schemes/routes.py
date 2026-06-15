from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.schemes.repository import (
    SchemeRepository,
)
from app.modules.schemes.schemas import (
    SchemeCreate,
    SchemeUpdate,
    SchemeResponse,
)
from app.modules.schemes.service import (
    SchemeService,
)

router = APIRouter()


@router.post(
    "",
    response_model=SchemeResponse,
)
async def create_scheme(
    scheme_data: SchemeCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = SchemeRepository(db)

    service = SchemeService(repository)

    return await service.create_scheme(
        scheme_data
    )


@router.get(
    "",
)
async def get_all_schemes(
    db: AsyncSession = Depends(get_db),
):
    repository = SchemeRepository(db)

    service = SchemeService(repository)

    return await service.get_all_schemes()


@router.get(
    "/{scheme_id}",
    response_model=SchemeResponse,
)
async def get_scheme(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
):
    repository = SchemeRepository(db)

    service = SchemeService(repository)

    return await service.get_scheme(
        scheme_id
    )


@router.put(
    "/{scheme_id}",
    response_model=SchemeResponse,
)
async def update_scheme(
    scheme_id: int,
    scheme_data: SchemeUpdate,
    db: AsyncSession = Depends(get_db),
):
    repository = SchemeRepository(db)

    service = SchemeService(repository)

    return await service.update_scheme(
        scheme_id,
        scheme_data,
    )