from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.modules.auth.dependencies import (
    get_current_user,
)

from app.modules.profile.repository import (
    ProfileRepository,
)
from app.modules.education.repository import (
    EducationRepository,
)
from app.modules.women.repository import (
    WomenRepository,
)
from app.modules.agriculture.repository import (
    AgricultureRepository,
)
from app.modules.schemes.repository import (
    SchemeRepository,
)

from app.modules.eligibility.schemas import (
    EligibleSchemeResponse,
)
from app.modules.eligibility.service import (
    EligibilityService,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[EligibleSchemeResponse],
)
async def get_eligible_schemes(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = EligibilityService(
        scheme_repository=SchemeRepository(db),
        profile_repository=ProfileRepository(db),
        education_repository=EducationRepository(db),
        women_repository=WomenRepository(db),
        agriculture_repository=AgricultureRepository(db),
    )

    return await service.get_eligible_schemes(
        current_user
    )