from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from schemas.module_schema import ModuleCreate, VendorAccessGrant, ModuleResponse
from services.module_service import ModuleService
from core.dependencies import get_current_user, require_super_admin
from services.document_service import DocumentService
import json

router = APIRouter(prefix="/modules", tags=["Modules (Global)"])

@router.post("", response_model=ModuleResponse)
async def create_module(payload: ModuleCreate, user=Depends(get_current_user)):
    require_super_admin(user)
    return await ModuleService.create_module(payload.name, payload.description, payload.system_prompt)

@router.post("/{module_id}/grant")
async def grant_vendor_access(module_id: str, payload: VendorAccessGrant, user=Depends(get_current_user)):
    require_super_admin(user)
    await ModuleService.grant_vendor_access(payload.vendor_id, module_id)
    return {"message": "Access granted successfully"}

from schemas.document_schema import JsonDocumentRequest

@router.post("/{module_id}/documents/json")
async def upload_module_json(module_id: str, payload: dict, user=Depends(get_current_user)):
    require_super_admin(user)
    
    # We allow the user to send standard JsonDocumentRequest format (pageContent, metadata)
    # But we map workspace_id to module_id, and vendor_id to "GLOBAL_MODULE"
    
    page_content = payload.get("pageContent", "")
    if not page_content:
        raise HTTPException(status_code=400, detail="Missing pageContent")
        
    doc_request = JsonDocumentRequest(
        workspace_id=module_id,
        vendor_id="00000000-0000-0000-0000-000000000000",
        pageContent=page_content,
        metadata=payload.get("metadata", {})
    )
    
    try:
        result = await DocumentService.ingest_json_document(
            payload=doc_request,
            uploaded_by=user["sub"]
        )
        return {"message": "JSON processed for module successfully", "chunks_created": result["chunks_created"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
