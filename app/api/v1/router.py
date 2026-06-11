from fastapi import APIRouter

from app.api.v1.routes import (
    action_plans,
    admin,
    auth,
    documents,
    eligibility,
    extraction,
    notifications,
    profiles,
    recommendations,
    schemes,
     saved_schemes,
        helper_sheets,
)

api_router = APIRouter()
for router in (
    auth.router,
    profiles.router,
    extraction.router,
    schemes.router,
    eligibility.router,
    recommendations.router,
    documents.router,
    action_plans.router,
    notifications.router,
     saved_schemes.router,
        helper_sheets.router,
    admin.router,
):
    api_router.include_router(router)

