from db.mongodb import db
from datetime import datetime, timezone
import uuid

class BillingRepository:
    vendor_billing = db["vendor_billing"]
    token_logs = db["token_logs"]

    @classmethod
    async def get_or_create_vendor_billing(cls, vendor_id: str):
        doc = await cls.vendor_billing.find_one({"vendor_id": vendor_id})
        if not doc:
            doc = {
                "vendor_id": vendor_id,
                "status": "active", # Default to active for new vendors
                "total_queries": 0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "created_at": datetime.now(timezone.utc)
            }
            await cls.vendor_billing.insert_one(doc)
            doc["_id"] = str(doc["_id"])
        else:
            doc["_id"] = str(doc["_id"])
        return doc

    @classmethod
    async def log_token_usage(
        cls, 
        vendor_id: str, 
        session_id: str, 
        model_name: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ):
        total_tokens = prompt_tokens + completion_tokens
        
        # 1. Insert immutable log
        log_doc = {
            "log_id": str(uuid.uuid4()),
            "vendor_id": vendor_id,
            "session_id": session_id,
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "timestamp": datetime.now(timezone.utc)
        }
        await cls.token_logs.insert_one(log_doc)
        
        # 2. Update vendor aggregate (upsert=True so new vendors are automatically created)
        await cls.vendor_billing.update_one(
            {"vendor_id": vendor_id},
            {
                "$inc": {
                    "total_queries": 1,
                    "total_prompt_tokens": prompt_tokens,
                    "total_completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                "$setOnInsert": {
                    "status": "active",
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        return True

    @classmethod
    async def update_vendor_status(cls, vendor_id: str, status: str):
        # status should be 'active' or 'inactive'
        result = await cls.vendor_billing.update_one(
            {"vendor_id": vendor_id},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
