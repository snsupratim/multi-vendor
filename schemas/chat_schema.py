from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    workspace_id: str
    question: str
    model_family: str = "gemini"
    model_name: str = "gemini-2.5-flash"
    session_id: Optional[str] = None