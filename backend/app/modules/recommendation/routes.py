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
from app.modules.documents.repository import (
    DocumentRepository,
)
from app.modules.schemes.repository import (
    SchemeRepository,
)

from app.modules.recommendation.schemas import (
    SchemeRecommendationResponse,
)
from app.modules.recommendation.service import (
    RecommendationService,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[
        SchemeRecommendationResponse
    ],
)
async def get_recommendations(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = RecommendationService(
        scheme_repository=SchemeRepository(db),
        profile_repository=ProfileRepository(db),
        education_repository=EducationRepository(db),
        women_repository=WomenRepository(db),
        agriculture_repository=AgricultureRepository(db),
        document_repository=DocumentRepository(db),
    )

    return await service.get_recommendations(
        current_user
    )