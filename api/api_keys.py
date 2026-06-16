from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from core.dependencies import (
    get_current_user,
    require_super_admin
)

from schemas.api_key_schema import (
    CreateApiKeyRequest
)

from services.api_key_service import (
    ApiKeyService
)

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"]
)


@router.post("")
async def create_api_key(
    payload: CreateApiKeyRequest,
    user=Depends(get_current_user)
):

    require_super_admin(user)

    return await (
        ApiKeyService.create_key(
            payload,
            user
        )
    )