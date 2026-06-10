from fastapi import Depends, FastAPI

from api.auth import router as auth_router
from api.vendors import router as vendor_router
from api.workspaces import (
    router as workspace_router
)


app = FastAPI(
    title="Multi Tenant RAG Platform"
)

app.include_router(auth_router)
app.include_router(vendor_router)
app.include_router(
    workspace_router
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }

