from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal
from app.dependencies.rbac import require_roles
from app.schemas.common import success_response
from app.schemas.documents import DocumentStatusUpdate
from app.schemas.scheme import (
    RequiredDocumentCreate,
    RuleCreate,
    RuleVersionCreate,
    SchemeCreate,
    SchemeUpdate,
)
from app.services.admin import AdminService
from app.services.documents import DocumentService
from app.services.schemes import SchemeQueryService
from app.utils.serialization import model_dict

router = APIRouter(prefix="/admin", tags=["Administration"])


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("/schemes")
async def list_all_schemes(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    data = await SchemeQueryService(session).list(
        limit=limit, offset=offset, include_inactive=True
    )
    return success_response(
        data=data, message="All schemes retrieved", trace_id=request.state.trace_id
    )


@router.post("/schemes", status_code=status.HTTP_201_CREATED)
async def create_scheme(
    payload: SchemeCreate,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    scheme = await AdminService(session).create_scheme(
        principal.user.id, payload, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(scheme),
        message="Scheme created",
        trace_id=request.state.trace_id,
    )


@router.patch("/schemes/{scheme_id}")
async def update_scheme(
    scheme_id: UUID,
    payload: SchemeUpdate,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    scheme = await AdminService(session).update_scheme(
        principal.user.id, scheme_id, payload, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(scheme),
        message="New scheme version created",
        trace_id=request.state.trace_id,
    )


@router.post("/schemes/{scheme_id}/enable")
async def enable_scheme(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    scheme = await AdminService(session).set_enabled(
        principal.user.id, scheme_id, True, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(scheme), message="Scheme enabled", trace_id=request.state.trace_id
    )


@router.post("/schemes/{scheme_id}/disable")
async def disable_scheme(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    scheme = await AdminService(session).set_enabled(
        principal.user.id, scheme_id, False, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(scheme), message="Scheme disabled", trace_id=request.state.trace_id
    )


@router.delete("/schemes/{scheme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheme(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    await AdminService(session).delete_scheme(
        principal.user.id, scheme_id, request.state.trace_id, _ip(request)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/schemes/{scheme_id}/rules", status_code=status.HTTP_201_CREATED)
async def create_rule(
    scheme_id: UUID,
    payload: RuleCreate,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    rule = await AdminService(session).add_rule(
        principal.user.id, scheme_id, payload, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(rule),
        message="Eligibility rule created",
        trace_id=request.state.trace_id,
    )


@router.post("/rules/{rule_id}/versions", status_code=status.HTTP_201_CREATED)
async def create_rule_version(
    rule_id: UUID,
    payload: RuleVersionCreate,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    version = await AdminService(session).add_rule_version(
        principal.user.id, rule_id, payload, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(version),
        message="Rule version created",
        trace_id=request.state.trace_id,
    )


@router.post(
    "/schemes/{scheme_id}/required-documents",
    status_code=status.HTTP_201_CREATED,
)
async def add_required_document(
    scheme_id: UUID,
    payload: RequiredDocumentCreate,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    document = await AdminService(session).add_required_document(
        principal.user.id, scheme_id, payload, request.state.trace_id, _ip(request)
    )
    return success_response(
        data=model_dict(document),
        message="Required document added",
        trace_id=request.state.trace_id,
    )


@router.patch("/users/{user_id}/documents/{document_id}")
async def verify_user_document(
    user_id: UUID,
    document_id: UUID,
    payload: DocumentStatusUpdate,
    request: Request,
    _: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    document = await DocumentService(session).update_status(user_id, document_id, payload)
    return success_response(
        data=model_dict(document),
        message="Document status updated",
        trace_id=request.state.trace_id,
    )


@router.get("/audit-logs")
async def audit_logs(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: Principal = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
):
    rows = await AdminService(session).list_audit_logs(limit, offset)
    return success_response(
        data=[model_dict(item) for item in rows],
        message="Audit logs retrieved",
        trace_id=request.state.trace_id,
    )

