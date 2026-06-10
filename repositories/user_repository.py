from db.mongodb import db


class UserRepository:

    collection = db["users"]

    @classmethod
    async def create_user(cls, data: dict):
        result = await cls.collection.insert_one(data)
        return str(result.inserted_id)

    @classmethod
    async def find_by_email(cls, email: str):
        return await cls.collection.find_one({"email": email})

    @classmethod
    async def find_by_id(cls, user_id: str):
        return await cls.collection.find_one({"_id": user_id})