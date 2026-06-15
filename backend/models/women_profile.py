from pydantic import BaseModel
from typing import Optional

class WomenProfile(BaseModel):
    user_id: str
    marital_status: Optional[str] = None
    pregnancy_status: Optional[str] = None
    lactating_mother: Optional[str] = None
    children: Optional[str] = None
    employment: Optional[str] = None
    selfhelp_group: Optional[str] = None
    disability: Optional[str] = None
    minority: Optional[str] = None
    housing: Optional[str] = None
    bank_account: Optional[str] = None
    government_benefits: Optional[str] = None
