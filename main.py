from fastapi import Depends, FastAPI

from api.auth import router as auth_router
from api.vendors import router as vendor_router
from api.workspaces import (
    router as workspace_router
)
from api.documents import (
    router as document_router
)
from api.chat import (
    router as chat_router
)
from core.monitoring import (
    init_sentry
)
from api.api_keys import (
    router as api_key_router
)

from api.public_chat import (
    router as public_chat_router
)

from middleware.logging_middleware import (
    LoggingMiddleware
)



init_sentry()

app = FastAPI(
    title="Multi Tenant RAG Platform"
)

app.include_router(auth_router)
app.include_router(vendor_router)
app.include_router(
    workspace_router
)

app.include_router(
    document_router
)



app.include_router(
    chat_router
)


app.include_router(
    api_key_router
)


app.include_router(
    public_chat_router
)

app.add_middleware(
    LoggingMiddleware
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }

@app.get("/test-sentry")
async def test_sentry():
    raise Exception(
        "Sentry Test Error"
    )