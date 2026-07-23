from pydantic import BaseModel, Field
from typing import Dict, Any

class JsonDocumentRequest(BaseModel):
    workspace_id: str
    vendor_id: str
    pageContent: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SqlSchemaRequest(BaseModel):
    workspace_id: str
    vendor_id: str
    table_name: str
    schema_ddl: str
    relationships: str = ""
    description: str = ""