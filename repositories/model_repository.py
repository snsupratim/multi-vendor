from db.mongodb import db

class ModelRepository:
    collection = db["models"]

    @classmethod
    async def create(cls, model_data: dict):
        await cls.collection.insert_one(model_data)

    @classmethod
    async def get_by_id(cls, model_id: str):
        return await cls.collection.find_one({"model_id": model_id})

    @classmethod
    async def get_by_name_and_family(cls, model_name: str, model_family: str):
        return await cls.collection.find_one({"model_name": model_name, "model_family": model_family})

    @classmethod
    async def get_all(cls):
        cursor = cls.collection.find({})
        return await cursor.to_list(length=None)

    @classmethod
    async def update(cls, model_id: str, update_data: dict):
        await cls.collection.update_one(
            {"model_id": model_id},
            {"$set": update_data}
        )

    @classmethod
    async def delete(cls, model_id: str):
        await cls.collection.delete_one({"model_id": model_id})
