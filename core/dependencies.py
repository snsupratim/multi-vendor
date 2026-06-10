from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt
from fastapi import HTTPException

from core.config import settings

security = HTTPBearer()


async def get_current_user(token=Depends(security)):

    payload = jwt.decode(
        token.credentials,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    return payload




def require_super_admin(user):

    if user["role"] != "SUPER_ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Only SUPER_ADMIN allowed"
        )