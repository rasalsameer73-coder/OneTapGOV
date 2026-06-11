import pytest

from app.dependencies.rbac import require_roles
from app.dependencies.auth import Principal
from app.core.exceptions import AuthorizationError


@pytest.mark.asyncio
async def test_require_roles_allows_admin():
    dep = require_roles("admin")
    principal = Principal(user=None, role="admin")
    result = await dep(principal)
    assert result is principal


@pytest.mark.asyncio
async def test_require_roles_denies_other():
    dep = require_roles("admin")
    principal = Principal(user=None, role="citizen")
    with pytest.raises(AuthorizationError):
        await dep(principal)
