from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from schemas.workspace_schema import (
    WorkspaceCreate
)

from services.workspace_service import (
    WorkspaceService
)

from core.dependencies import (
    get_current_user,
    require_super_admin
)

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


@router.post("")
async def create_workspace(
    payload: WorkspaceCreate,
    user=Depends(get_current_user)
):

    try:

        require_super_admin(user)

        return await WorkspaceService.create_workspace(
            payload,
            user
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/vendor/{vendor_id}")
async def get_vendor_workspaces(
    vendor_id: str,
    user=Depends(get_current_user)
):

    require_super_admin(user)

    return (
        await WorkspaceService
        .get_vendor_workspaces(vendor_id)
    )