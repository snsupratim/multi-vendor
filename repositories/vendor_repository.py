from db.mongodb import db


class VendorRepository:

    collection = db["vendors"]

    @classmethod
    async def create_vendor(cls, vendor_data: dict):
        await cls.collection.insert_one(vendor_data)

    @classmethod
    async def find_by_name(cls, name: str):
        return await cls.collection.find_one(
            {"name": name}
        )

    @classmethod
    async def get_all(cls):
        cursor = cls.collection.find()

        return await cursor.to_list(
            length=None
        )

    @classmethod
    async def get_by_vendor_id(
        cls,
        vendor_id: str
    ):
        return await cls.collection.find_one(
            {"vendor_id": vendor_id}
        )