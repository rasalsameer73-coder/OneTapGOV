from pydantic import BaseModel
from typing import Optional

class FarmerProfile(BaseModel):
    user_id: str
    agricultural_land: Optional[str] = None
    area: Optional[str] = None
    registered_in_your_name: Optional[str] = None
    primary_occu: Optional[str] = None
    crops: Optional[str] = None
    source_of_irrigation: Optional[str] = None
    bank_account: Optional[str] = None
    gov_records: Optional[str] = None
    live_stock: Optional[str] = None
    agri_machinery: Optional[str] = None
