from fastapi import FastAPI

from app.core.config import settings
from app.core.lifespan import lifespan

from app.modules.auth.routes import (
    router as auth_router,
)
from app.modules.profile.routes import (
    router as profile_router,
)
from app.modules.education.routes import (
    router as education_router,
)
from app.modules.women.routes import (
    router as women_router,
)
from app.modules.agriculture.routes import (
    router as agriculture_router,
)
from app.modules.schemes.routes import (
    router as scheme_router,
)
from app.modules.eligibility.routes import (
    router as eligibility_router,
)
from app.modules.documents.routes import (
    router as document_router,
)
from app.modules.recommendation.routes import (
    router as recommendation_router,
)
from app.modules.user_documents.routes import (
    router as user_document_router,
)
from app.modules.readiness.routes import (
    router as readiness_router,
)
from app.modules.assistant.routes import (
    router as assistant_router,
)
from app.modules.admin.routes import (
    router as admin_router,
)


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "OneTapGOV Backend Running"
    }


app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    profile_router,
    prefix="/api/v1/profile",
    tags=["Profile"],
)

app.include_router(
    education_router,
    prefix="/api/v1/education",
    tags=["Education"],
)

app.include_router(
    women_router,
    prefix="/api/v1/women",
    tags=["Women Welfare"],
)

app.include_router(
    agriculture_router,
    prefix="/api/v1/agriculture",
    tags=["Agriculture"],
)

app.include_router(
    scheme_router,
    prefix="/api/v1/schemes",
    tags=["Schemes"],
)

app.include_router(
    eligibility_router,
    prefix="/api/v1/eligibility",
    tags=["Eligibility"],
)

app.include_router(
    document_router,
    prefix="/api/v1/documents",
    tags=["Documents"],
)

app.include_router(
    recommendation_router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"],
)

app.include_router(
    user_document_router,
    prefix="/api/v1/user-documents",
    tags=["User Documents"],
)

app.include_router(
    readiness_router,
    prefix="/api/v1/readiness",
    tags=["Readiness"],
)

app.include_router(
    assistant_router,
    prefix="/api/v1/assistant",
    tags=["AI Assistant"],
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Admin"],
)