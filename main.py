from fastapi import Depends, FastAPI
import core.logger  # Initialize global loguru configuration

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

from api.api_keys import (
    router as api_key_router
)

from api.public_chat import (
    router as public_chat_router
)

from api.redis_test import (
    router as redis_test_router
)
from api.api_keys import (
    router as api_key_router
)

from api.models import (
    router as model_router
)
# from services.model_router import ModelRouter


from middleware.logging_middleware import (
    APMMiddleware
)




app = FastAPI(
    title="Multi Tenant RAG Platform"
)


# print(
#     ModelRouter.generate(
#         prompt="What is Python?",
#         model_name="llama-3.3-70b-versatile"
#     )
# )

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

app.include_router(
    redis_test_router
)

app.include_router(
    model_router
)

from api.logs import router as logs_router
app.include_router(
    logs_router
)

from api.modules import router as modules_router
from api.module_chat import router as module_chat_router
from api.public_module_chat import router as public_module_chat_router

app.include_router(modules_router)
app.include_router(module_chat_router)
app.include_router(public_module_chat_router)

app.add_middleware(
    APMMiddleware
)

import asyncio
from core.mongo_sink import start_mongo_logger
from core.apm import start_apm_worker

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_mongo_logger())
    asyncio.create_task(start_apm_worker())


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }

@app.get("/test-apm")
async def test_apm():
    raise Exception(
        "APM Test Error"
    )

