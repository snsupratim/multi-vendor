from pydantic import BaseModel, Field
from typing import Optional


class WorkspaceCreate(BaseModel):
    vendor_id: str

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    workspace_id: str
    vendor_id: str
    name: str
    status: str