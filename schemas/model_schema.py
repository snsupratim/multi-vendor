from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ModelCreate(BaseModel):
    model_family: str = Field(..., description="E.g., llama-3, gemini, qwen")
    model_name: str = Field(..., description="E.g., llama-3.1-8b-instant")
    provider: str = Field(..., description="E.g., groq, gemini")
    display_name: str = Field(..., description="Display Name")

class ModelUpdate(BaseModel):
    model_family: Optional[str] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    display_name: Optional[str] = None

class ModelResponse(ModelCreate):
    model_id: str
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
