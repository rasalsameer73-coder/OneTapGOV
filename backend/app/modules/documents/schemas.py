from pydantic import BaseModel, ConfigDict


class SchemeDocumentCreate(BaseModel):
    scheme_id: int
    document_name: str
    is_mandatory: bool = True
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scheme_id": 1,
                "document_name": "Aadhaar Card",
                "is_mandatory": True,
            }
        }
    )


class SchemeDocumentResponse(BaseModel):
    id: int
    scheme_id: int
    document_name: str
    is_mandatory: bool

    model_config = ConfigDict(
        from_attributes=True
    )