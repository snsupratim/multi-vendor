from pydantic import BaseModel, Field
from typing import Optional


class VendorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class VendorResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str