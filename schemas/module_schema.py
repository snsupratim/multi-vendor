from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModuleCreate(BaseModel):
    name: str # e.g. "PAYROLL"
    description: Optional[str] = None
    system_prompt: Optional[str] = None

class ModuleResponse(ModuleCreate):
    module_id: str
    created_at: datetime

class VendorAccessGrant(BaseModel):
    vendor_id: str

class ModuleChatRequest(BaseModel):
    module_id: str
    vendor_id: str
    question: str
    model_family: Optional[str] = "gemini"
    model_name: Optional[str] = "gemini-2.5-flash"
    session_id: Optional[str] = None
