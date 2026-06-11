from typing import Callable

from fastapi import Depends

from app.dependencies.auth import Principal, get_current_principal
from app.core.exceptions import AuthorizationError


def require_roles(*allowed_roles: str) -> Callable:
    """Return a dependency that enforces the given roles.

    Usage:
        @router.get("/admin")
        async def admin_only(principal: Principal = Depends(require_roles("admin"))):
            ...
    """

    async def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if principal.role not in allowed_roles:
            raise AuthorizationError(f"Required role(s): {', '.join(allowed_roles)}")
        return principal

    return dependency
