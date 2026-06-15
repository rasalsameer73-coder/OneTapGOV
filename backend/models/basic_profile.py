from pydantic import BaseModel
from typing import Optional

class BasicProfile(BaseModel):
    user_id: str
    preferred_language: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    income: Optional[float] = None
    category: Optional[str] = None
    sector: Optional[str] = None
