from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_current_user, require_super_admin
from services.billing_service import BillingService
from pydantic import BaseModel

router = APIRouter(prefix="/billing", tags=["Tenant Billing & Token Tracking"])

class StatusUpdatePayload(BaseModel):
    status: str # "active" or "inactive"

@router.get("/{vendor_id}")
async def get_billing_stats(vendor_id: str, user=Depends(get_current_user)):
    """
    Retrieve token usage stats for a specific vendor.
    """
    require_super_admin(user)
    stats = await BillingService.get_vendor_stats(vendor_id)
    return stats

@router.put("/{vendor_id}/status")
async def update_vendor_status(vendor_id: str, payload: StatusUpdatePayload, user=Depends(get_current_user)):
    """
    Block or unblock a vendor by setting their status to 'active' or 'inactive'.
    """
    require_super_admin(user)
    try:
        success = await BillingService.update_vendor_status(vendor_id, payload.status)
        if success:
            return {"message": f"Vendor {vendor_id} is now {payload.status}"}
        raise HTTPException(status_code=400, detail="Failed to update status")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
