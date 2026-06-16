from fastapi import APIRouter

from services.model_registry import (
    SUPPORTED_MODELS
)

router = APIRouter(
    prefix="/models",
    tags=["Models"]
)


@router.get("")
async def list_models():

    return SUPPORTED_MODELS