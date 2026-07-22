from db.mongodb import db
from datetime import datetime, timezone

class LogRepository:
    collection = db["system_logs"]

    @classmethod
    async def append_log(cls, log_data: dict):
        # Extract timestamp or use current time
        now = datetime.now(timezone.utc)
        # Create an hour string for the bucket, e.g. "2026-07-22-22"
        hour_bucket = now.strftime("%Y-%m-%d-%H")
        
        await cls.collection.update_one(
            {"hour": hour_bucket},
            {
                "$setOnInsert": {"created_at": now},
                "$push": {"logs": log_data}
            },
            upsert=True
        )

    @classmethod
    async def get_logs(
        cls,
        vendor_id: str = None,
        workspace_id: str = None,
        session_id: str = None,
        limit: int = 100
    ):
        match_stage = {}
        if vendor_id:
            match_stage["logs.vendor_id"] = vendor_id
        if workspace_id:
            match_stage["logs.workspace_id"] = workspace_id
        if session_id:
            match_stage["logs.session_id"] = session_id
        
        pipeline = [
            {"$unwind": "$logs"}
        ]
        
        if match_stage:
            pipeline.append({"$match": match_stage})
            
        pipeline.extend([
            {"$sort": {"logs.timestamp": -1}},
            {"$limit": limit},
            {"$replaceRoot": {"newRoot": "$logs"}}
        ])
        
        cursor = cls.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
