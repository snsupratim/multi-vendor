from db.mongodb import db


class UsageRepository:

    collection = db["usage_logs"]

    @classmethod
    async def create(
        cls,
        document: dict
    ):
        await cls.collection.insert_one(
            document
        )