from fastapi import APIRouter, Depends
from schemas.module_schema import ModuleChatRequest
from services.module_rag_service import ModuleRAGService
from core.api_key_dependency import get_api_key_context
import uuid


router = APIRouter(prefix="/v1/public/module-chat", tags=["Module Chat (Public)"])

@router.post("")
async def public_module_chat(payload: ModuleChatRequest, api_context=Depends(get_api_key_context)):
    vendor_id = api_context["vendor_id"]
    session_id = payload.session_id or str(uuid.uuid4())
    
    result = await ModuleRAGService.ask(
        question=payload.question,
        module_id=payload.module_id,
        vendor_id=vendor_id,
        model_family=payload.model_family,
        model_name=payload.model_name,
        session_id=session_id
    )
    

    
    return result
