from db.mongodb import db
from datetime import datetime, timezone

class VendorAccessRepository:
    collection = db["vendor_module_access"]

    @classmethod
    async def grant_access(cls, vendor_id: str, module_id: str):
        await cls.collection.update_one(
            {"vendor_id": vendor_id, "module_id": module_id},
            {"$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True
        )

    @classmethod
    async def revoke_access(cls, vendor_id: str, module_id: str):
        await cls.collection.delete_one({"vendor_id": vendor_id, "module_id": module_id})

    @classmethod
    async def check_access(cls, vendor_id: str, module_id: str) -> bool:
        # Temporarily bypassed: All vendors have universal access to all modules
        return True
