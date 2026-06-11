from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPAuthorizationCredentials

from app.core.database import AsyncSessionFactory
from app.dependencies.auth import get_current_principal


class PrincipalMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.principal = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            async with AsyncSessionFactory() as session:
                try:
                    principal = await get_current_principal(creds, session)
                    request.state.principal = principal
                except Exception:
                    request.state.principal = None
        return await call_next(request)
