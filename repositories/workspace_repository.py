from db.mongodb import db


class WorkspaceRepository:

    collection = db["workspaces"]

    @classmethod
    async def create_workspace(
        cls,
        workspace_data: dict
    ):
        await cls.collection.insert_one(
            workspace_data
        )

    @classmethod
    async def get_by_workspace_id(
        cls,
        workspace_id: str
    ):
        return await cls.collection.find_one(
            {
                "workspace_id": workspace_id
            }
        )

    @classmethod
    async def get_by_vendor(
        cls,
        vendor_id: str
    ):
        cursor = cls.collection.find(
            {
                "vendor_id": vendor_id
            }
        )

        return await cursor.to_list(
            length=None
        )

    @classmethod
    async def exists(
        cls,
        vendor_id: str,
        workspace_name: str
    ):
        return await cls.collection.find_one(
            {
                "vendor_id": vendor_id,
                "name": workspace_name
            }
        )