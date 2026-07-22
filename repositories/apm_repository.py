from db.mongodb import db
from datetime import datetime, timezone

class APMRepository:
    errors_collection = db["apm_errors"]
    performance_collection = db["apm_performance"]

    @classmethod
    async def append_error(cls, error_data: dict):
        now = datetime.now(timezone.utc)
        hour_bucket = now.strftime("%Y-%m-%d-%H")
        
        await cls.errors_collection.update_one(
            {"hour": hour_bucket},
            {
                "$setOnInsert": {"created_at": now},
                "$push": {"errors": error_data}
            },
            upsert=True
        )

    @classmethod
    async def append_performance(cls, perf_data: dict):
        now = datetime.now(timezone.utc)
        hour_bucket = now.strftime("%Y-%m-%d-%H")
        
        await cls.performance_collection.update_one(
            {"hour": hour_bucket},
            {
                "$setOnInsert": {"created_at": now},
                "$push": {"metrics": perf_data}
            },
            upsert=True
        )
