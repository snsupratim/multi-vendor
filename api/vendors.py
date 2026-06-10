from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from schemas.vendor_schema import VendorCreate

from services.vendor_service import VendorService

from core.dependencies import (
    get_current_user,
    require_super_admin
)

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"]
)


@router.post("")
async def create_vendor(
    payload: VendorCreate,
    user=Depends(get_current_user)
):

    try:

        require_super_admin(user)

        return await VendorService.create_vendor(
            payload,
            user
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("")
async def get_all_vendors(
    user=Depends(get_current_user)
):

    require_super_admin(user)

    return await VendorService.get_all_vendors()


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: str,
    user=Depends(get_current_user)
):

    require_super_admin(user)

    return await VendorService.get_vendor(
        vendor_id
    )