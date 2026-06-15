from pydantic import BaseModel, ConfigDict


class SchemeCreate(BaseModel):
    scheme_name: str
    scheme_code: str

    description: str | None = None
    department: str | None = None
    state: str | None = None
    official_url: str | None = None


class SchemeUpdate(BaseModel):
    scheme_name: str
    scheme_code: str

    description: str | None = None
    department: str | None = None
    state: str | None = None
    official_url: str | None = None

    is_active: bool = True


class SchemeResponse(BaseModel):
    id: int

    scheme_name: str
    scheme_code: str

    description: str | None
    department: str | None
    state: str | None
    official_url: str | None

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )