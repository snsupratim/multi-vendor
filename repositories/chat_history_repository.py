from db.mongodb import db

class ChatHistoryRepository:
    collection = db["chat_history"]

    @classmethod
    async def append_message(
        cls,
        session_id: str,
        vendor_id: str,
        role: str,
        content: str,
        timestamp: str
    ):
        await cls.collection.insert_one({
            "session_id": session_id,
            "vendor_id": vendor_id,
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

    @classmethod
    async def get_sessions(cls, vendor_id: str):
        pipeline = [
            {"$match": {"vendor_id": vendor_id}},
            {"$sort": {"timestamp": 1}},
            {"$group": {
                "_id": "$session_id",
                "title": {"$first": "$content"},
                "last_active": {"$last": "$timestamp"}
            }},
            {"$sort": {"last_active": -1}}
        ]
        cursor = cls.collection.aggregate(pipeline)
        sessions = await cursor.to_list(length=None)
        
        # Format the output for the API
        return [
            {
                "session_id": s["_id"],
                "title": s["title"][:50] + "..." if len(s["title"]) > 50 else s["title"],
                "last_active": s["last_active"]
            }
            for s in sessions
        ]

    @classmethod
    async def get_session_messages(cls, session_id: str):
        cursor = cls.collection.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1)
        
        docs = await cursor.to_list(length=None)
        return docs
