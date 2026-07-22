import uuid
from datetime import datetime, timezone

from repositories.workspace_repository import (
    WorkspaceRepository
)

from repositories.vendor_repository import (
    VendorRepository
)


class WorkspaceService:

    @staticmethod
    async def create_workspace(
        payload,
        user
    ):

        vendor = await VendorRepository.get_by_vendor_id(
            payload.vendor_id
        )

        if not vendor:
            raise ValueError(
                "Vendor not found"
            )

        existing = await WorkspaceRepository.exists(
            payload.vendor_id,
            payload.name
        )

        if existing:
            raise ValueError(
                "Workspace already exists"
            )

        workspace = {
            "workspace_id": str(uuid.uuid4()),
            "vendor_id": payload.vendor_id,
            "name": payload.name,
            "description": payload.description,
            "status": "ACTIVE",
            "created_by": user["sub"],
            "created_at": datetime.now(
                timezone.utc
            ),
            "system_prompt": getattr(payload, "system_prompt", None)
        }

        await WorkspaceRepository.create_workspace(
            workspace
        )

        return {
            "workspace_id": workspace["workspace_id"],
            "message": "Workspace created"
        }

    @staticmethod
    async def get_vendor_workspaces(
        vendor_id: str
    ):

        workspaces = (
            await WorkspaceRepository
            .get_by_vendor(vendor_id)
        )

        response = []

        for workspace in workspaces:

            response.append({
                "workspace_id": workspace["workspace_id"],
                "vendor_id": workspace["vendor_id"],
                "name": workspace["name"],
                "description": workspace.get("description"),
                "status": workspace["status"],
                "system_prompt": workspace.get("system_prompt")
            })

        return response

    @staticmethod
    async def update_prompt(
        workspace_id: str,
        system_prompt: str
    ):
        workspace = await WorkspaceRepository.get_by_workspace_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
            
        await WorkspaceRepository.update_workspace(
            workspace_id,
            {"system_prompt": system_prompt}
        )
        return {"message": "System prompt updated successfully"}