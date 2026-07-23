from db.mongodb import db
from datetime import datetime, timezone
import uuid

class ModuleRepository:
    collection = db["modules"]

    @classmethod
    async def create_module(cls, name: str, description: str = None, system_prompt: str = None):
        module_id = str(uuid.uuid4())
        doc = {
            "module_id": module_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "created_at": datetime.now(timezone.utc)
        }
        await cls.collection.insert_one(doc)
        doc["_id"] = str(doc["_id"])
        return doc

    @classmethod
    async def get_by_module_id(cls, module_id: str):
        return await cls.collection.find_one({"module_id": module_id})
