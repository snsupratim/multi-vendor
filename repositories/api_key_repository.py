from db.mongodb import db


class ApiKeyRepository:

    collection = db["api_keys"]

    @classmethod
    async def create(cls, data: dict):
        await cls.collection.insert_one(data)

    @classmethod
    async def get_by_hash(cls, api_key_hash: str):
        return await cls.collection.find_one(
            {
                "api_key_hash": api_key_hash,
                "status": "ACTIVE"
            }
        )

    @classmethod
    async def get_all(cls):
        cursor = cls.collection.find()

        return await cursor.to_list(length=None)
    
    