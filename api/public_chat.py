from fastapi import APIRouter, Depends

from core.api_key_dependency import (
    get_api_key_context
)

from schemas.public_chat_schema import (
    PublicChatRequest
)

from services.rag_service import (
    RAGService
)

router = APIRouter(
    prefix="/v1/public",
    tags=["Public Chat"]
)


@router.post("/chat")
async def public_chat(
    payload: PublicChatRequest,
    api_context=Depends(
        get_api_key_context
    )
):

    answer = RAGService.ask(
        question=payload.question,
        workspace_id=api_context["workspace_id"]
    )

    return {
        "answer": answer,
        # "workspace_id": api_context["workspace_id"],
        # "vendor_id": api_context["vendor_id"]
    }