from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_current_user, require_super_admin
from repositories.log_repository import LogRepository

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

@router.get("")
async def get_all_logs(user=Depends(get_current_user)):
    try:
        require_super_admin(user)
        return await LogRepository.get_logs(limit=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/vendor/{vendor_id}")
async def get_vendor_logs(vendor_id: str, user=Depends(get_current_user)):
    try:
        require_super_admin(user)
        return await LogRepository.get_logs(vendor_id=vendor_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workspace/{workspace_id}")
async def get_workspace_logs(workspace_id: str, user=Depends(get_current_user)):
    try:
        require_super_admin(user)
        return await LogRepository.get_logs(workspace_id=workspace_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_logs(session_id: str, user=Depends(get_current_user)):
    try:
        require_super_admin(user)
        return await LogRepository.get_logs(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
