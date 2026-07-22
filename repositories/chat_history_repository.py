from db.mongodb import db

class ChatHistoryRepository:
    collection = db["chat_history"]

    @classmethod
    async def append_message(
        cls,
        session_id: str,
        role: str,
        content: str,
        timestamp: str
    ):
        await cls.collection.insert_one({
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": timestamp
        })

    @classmethod
    async def get_recent_history(
        cls,
        session_id: str,
        limit: int = 5
    ):
        # Fetch up to `limit` pairs (limit * 2 docs)
        cursor = cls.collection.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit * 2)
        
        docs = await cursor.to_list(length=None)
        docs.reverse() # Put back into chronological order
        
        return docs
