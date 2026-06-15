from app.modules.schemes.models import Scheme
from app.modules.schemes.repository import (
    SchemeRepository,
)
from app.modules.schemes.schemas import (
    SchemeCreate,
    SchemeUpdate,
)


class SchemeService:

    def __init__(
        self,
        repository: SchemeRepository,
    ):
        self.repository = repository

    async def create_scheme(
        self,
        scheme_data: SchemeCreate,
    ) -> Scheme:

        scheme = Scheme(
            scheme_name=scheme_data.scheme_name,
            scheme_code=scheme_data.scheme_code,
            description=scheme_data.description,
            department=scheme_data.department,
            state=scheme_data.state,
            official_url=scheme_data.official_url,
        )

        return await self.repository.create_scheme(
            scheme
        )

    async def get_scheme(
        self,
        scheme_id: int,
    ):

        return await self.repository.get_scheme_by_id(
            scheme_id
        )

    async def get_all_schemes(
        self,
    ):

        return await self.repository.get_all_schemes()

    async def update_scheme(
        self,
        scheme_id: int,
        scheme_data: SchemeUpdate,
    ):

        scheme = await self.repository.get_scheme_by_id(
            scheme_id
        )

        if not scheme:
            raise ValueError(
                "Scheme not found"
            )

        scheme.scheme_name = scheme_data.scheme_name
        scheme.scheme_code = scheme_data.scheme_code
        scheme.description = scheme_data.description
        scheme.department = scheme_data.department
        scheme.state = scheme_data.state
        scheme.official_url = scheme_data.official_url
        scheme.is_active = scheme_data.is_active

        return await self.repository.update_scheme(
            scheme
        )