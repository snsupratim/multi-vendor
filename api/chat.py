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

    import uuid
    session_id = payload.session_id if payload.session_id else str(uuid.uuid4())

    return await (
        RAGService.ask(
            payload.question,
            payload.workspace_id,
            payload.model_family,
            payload.model_name,
            session_id
        )
    )