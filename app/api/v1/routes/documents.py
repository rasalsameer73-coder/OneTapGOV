from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import Principal, get_current_principal
from app.schemas.common import success_response
from app.schemas.documents import UserDocumentCreate
from app.services.documents import DocumentService
from app.utils.serialization import model_dict
import tempfile
from fastapi import UploadFile, File
import shutil
import os

router = APIRouter(prefix="/documents", tags=["Documents and Readiness"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: UserDocumentCreate,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    document = await DocumentService(session).create(principal.user.id, payload)
    return success_response(
        data=model_dict(document),
        message="Document metadata recorded; OCR was not performed",
        trace_id=request.state.trace_id,
    )


@router.get("")
async def list_documents(
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    documents = await DocumentService(session).list(principal.user.id)
    return success_response(
        data=[model_dict(item) for item in documents],
        message="Documents retrieved",
        trace_id=request.state.trace_id,
    )


@router.get("/readiness/{scheme_id}")
async def readiness(
    scheme_id: UUID,
    request: Request,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    data = await DocumentService(session).readiness(principal.user.id, scheme_id)
    return success_response(
        data=data, message="Readiness calculated", trace_id=request.state.trace_id
    )


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_code: str | None = None,
    name: str | None = None,
    request: Request = None,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    # Save to a temporary location and return a storage_key placeholder
    # Use configured storage provider (Supabase if configured, else local)
    from app.services.storage import get_storage_provider
    from app.services.ocr import get_ocr_provider
    from app.services.extraction import AIExtractionService
    from structlog import get_logger

    logger = get_logger()

    provider = get_storage_provider()
    storage_key, public_url = provider.upload(file.filename, file.file)

    payload = UserDocumentCreate(
        document_code=(document_code or "UNKNOWN"), name=(name or file.filename), storage_key=storage_key
    )
    document = await DocumentService(session).create(principal.user.id, payload)

    # Optionally perform OCR and AI extraction
    ocr_text = None
    extracted = None
    if request and request.query_params.get("perform_ocr") in {"1", "true", "True"}:
        ocr_provider = get_ocr_provider()
        try:
            ocr_text = ocr_provider.extract_text(storage_key if isinstance(storage_key, str) else storage_key)
        except Exception:
            ocr_text = ""
    if request and request.query_params.get("perform_extraction") in {"1", "true", "True"}:
        # Use AIExtractionService; provider selection is internal
        try:
            result = await AIExtractionService(session).extract(principal.user.id, ocr_text or "")
            extracted = result.model_dump(mode="json")
        except Exception:
            extracted = None

    response = model_dict(document)
    response.update({"storage_url": public_url, "ocr_text": ocr_text, "extracted": extracted})
    logger.info("upload.complete", user_id=str(principal.user.id), storage_key=storage_key)
    return success_response(
        data=response,
        message="File uploaded and document recorded",
        trace_id=request.state.trace_id if request else None,
    )

