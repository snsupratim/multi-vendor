import json
from datetime import datetime, timezone
from db.redis import redis_client
from repositories.chat_history_repository import ChatHistoryRepository

class MemoryService:
    TTL_SECONDS = 7200 # 2 hours
    HISTORY_LIMIT = 10 # 5 pairs of Q&A

    @staticmethod
    def _get_key(session_id: str):
        return f"chat_memory:{session_id}"

    @classmethod
    async def get_history(cls, session_id: str) -> str:
        key = cls._get_key(session_id)
        
        # 1. Try Redis first (Short-Term Memory)
        history_list = await redis_client.lrange(key, 0, -1)
        
        if not history_list:
            # 2. Rehydrate from MongoDB (Long-Term Memory)
            docs = await ChatHistoryRepository.get_recent_history(session_id, limit=cls.HISTORY_LIMIT // 2)
            if not docs:
                return ""
                
            # Rehydrate Redis
            for doc in docs:
                msg_str = json.dumps({"role": doc["role"], "content": doc["content"]})
                await redis_client.rpush(key, msg_str)
                history_list.append(msg_str)
                
            await redis_client.expire(key, cls.TTL_SECONDS)
        
        # Format history into a string
        formatted = []
        for item in history_list:
            msg = json.loads(item)
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
            
        return "\n".join(formatted)

    @classmethod
    async def save_turn(cls, session_id: str, vendor_id: str, question: str, answer: str):
        key = cls._get_key(session_id)
        now = datetime.now(timezone.utc).isoformat()
        
        q_msg = {"role": "user", "content": question}
        a_msg = {"role": "assistant", "content": answer}
        
        # 1. Save to Redis
        await redis_client.rpush(key, json.dumps(q_msg), json.dumps(a_msg))
        # Keep only the last HISTORY_LIMIT messages
        await redis_client.ltrim(key, -cls.HISTORY_LIMIT, -1)
        await redis_client.expire(key, cls.TTL_SECONDS)
        
        # 2. Save to MongoDB
        await ChatHistoryRepository.append_message(session_id, vendor_id, "user", question, now)
        await ChatHistoryRepository.append_message(session_id, vendor_id, "assistant", answer, now)
