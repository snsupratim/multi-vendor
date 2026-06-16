from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    chunks_created: int