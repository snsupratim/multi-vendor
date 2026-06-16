from fastapi import Header, HTTPException

from services.api_key_service import ApiKeyService


async def get_api_key_context(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    api_key = await ApiKeyService.validate_key(
        x_api_key
    )

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    if api_key.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="API Key is inactive"
        )

    return api_key