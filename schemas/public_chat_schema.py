from pydantic import BaseModel
from typing import Optional

class PublicChatRequest(BaseModel):
    question: str
    model_family: str = "gemini"
    model_name: str = "gemini-2.5-flash"
    session_id: Optional[str] = None