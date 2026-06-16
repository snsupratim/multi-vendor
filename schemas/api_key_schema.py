from pydantic import BaseModel


class CreateApiKeyRequest(BaseModel):
    # vendor_id: str
    workspace_id: str
    name: str


class CreateApiKeyResponse(BaseModel):
    api_key: str
    api_key_id: str