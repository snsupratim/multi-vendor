from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import get_current_user
from schemas.user_schema import (
    UserCreate,
    UserLogin
)

from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
async def register(payload: UserCreate):
    try:
        return await AuthService.register(payload)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
async def login(payload: UserLogin):
    try:
        return await AuthService.login(payload)

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user