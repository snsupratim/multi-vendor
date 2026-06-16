from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)

db = client["rag_platform"]
api_keys_db = client["api_keys"]