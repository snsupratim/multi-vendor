from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_current_user, require_super_admin
from schemas.model_schema import ModelCreate, ModelUpdate, ModelResponse
from services.model_service import ModelService

router = APIRouter(
    prefix="/models",
    tags=["Models"]
)

@router.post("", response_model=ModelResponse)
async def create_model(
    payload: ModelCreate,
    user=Depends(get_current_user)
):
    try:
        require_super_admin(user)
        return await ModelService.create_model(payload, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_models():
    return await ModelService.get_all_models()

@router.get("/{model_id}")
async def get_model(model_id: str):
    try:
        return await ModelService.get_model(model_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    payload: ModelUpdate,
    user=Depends(get_current_user)
):
    try:
        require_super_admin(user)
        return await ModelService.update_model(model_id, payload, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    user=Depends(get_current_user)
):
    try:
        require_super_admin(user)
        return await ModelService.delete_model(model_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))