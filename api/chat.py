from fastapi import (
    APIRouter,
    Depends
)

from schemas.chat_schema import (
    ChatRequest
)

from services.rag_service import (
    RAGService
)

from core.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("")
async def chat(
    payload: ChatRequest,
    user=Depends(
        get_current_user
    )
):

    return (
        RAGService.ask(
            payload.question,
            payload.workspace_id,
            payload.model
        )
    )