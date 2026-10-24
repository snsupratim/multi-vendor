from fastapi import APIRouter
from schemas.module_schema import ModuleChatRequest
from services.module_rag_service import ModuleRAGService
import uuid

router = APIRouter(prefix="/module-chat", tags=["Module Chat (Internal)"])

@router.post("")
async def internal_module_chat(payload: ModuleChatRequest):
    vendor_id = payload.vendor_id
    session_id = payload.session_id or str(uuid.uuid4())
    
    result = await ModuleRAGService.ask(
        question=payload.question,
        module_id=payload.module_id,
        vendor_id=vendor_id,
        model_family=payload.model_family,
        model_name=payload.model_name,
        session_id=session_id,
        user_context=payload.user_context
    )
    
    return result
