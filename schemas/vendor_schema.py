from pydantic import BaseModel, Field
from typing import Optional


class VendorCreate(BaseModel):
    id: Optional[str] = Field(None, description="Optional custom vendor ID")
    vendor_id: Optional[str] = Field(None, description="Optional custom vendor ID")
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class VendorResponse(BaseModel):
    id: str
    vendor_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str