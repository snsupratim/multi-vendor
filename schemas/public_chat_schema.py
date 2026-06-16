# schemas/public_chat_schema.py

from pydantic import BaseModel


class PublicChatRequest(BaseModel):
    question: str