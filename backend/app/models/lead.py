from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    client_id: str
    session_id: str
    message: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
