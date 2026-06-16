from pydantic import BaseModel


class ChatRequest(BaseModel):
    workspace_id: str
    question: str
    model: str = (
        "gemini-2.5-flash"
    )