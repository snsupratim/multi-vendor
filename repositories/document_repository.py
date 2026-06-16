from db.mongodb import db


class DocumentRepository:

    collection = db["documents"]

    @classmethod
    async def create_document(
        cls,
        document_data: dict
    ):
        await cls.collection.insert_one(
            document_data
        )

    @classmethod
    async def get_document(
        cls,
        document_id: str
    ):
        return await cls.collection.find_one(
            {
                "document_id": document_id
            }
        )

    @classmethod
    async def find_by_file_name(
        cls,
        file_name: str,
        workspace_id: str
    ):
        return await cls.collection.find_one(
            {
                "file_name": file_name,
                "workspace_id": workspace_id
            }
        )