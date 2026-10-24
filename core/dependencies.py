from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt
from fastapi import HTTPException
import sentry_sdk
from core.config import settings

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(token=Depends(security)):

    payload = jwt.decode(
        token.credentials,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    sentry_sdk.set_user(
        {
            "email": payload["sub"]
        }
    )

    return payload


async def get_optional_current_user(token=Depends(optional_security)):
    if not token or not token.credentials:
        return None
    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except Exception:
        return None




def require_super_admin(user):

    if user["role"] != "SUPER_ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Only SUPER_ADMIN allowed"
        )