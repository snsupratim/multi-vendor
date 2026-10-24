import json
from typing import Optional
from datetime import datetime, timezone
from db.redis import redis_client
from repositories.chat_history_repository import ChatHistoryRepository
from loguru import logger

class MemoryService:
    TTL_SECONDS = 7200 # 2 hours
    HISTORY_LIMIT = 10 # 5 pairs of Q&A

    @staticmethod
    def _get_key(session_id: str):
        return f"chat_memory:{session_id}"

    @classmethod
    async def get_history(cls, session_id: str) -> str:
        key = cls._get_key(session_id)
        history_list = []
        
        # 1. Try Redis first (Short-Term Memory Cache)
        try:
            history_list = await redis_client.lrange(key, 0, -1)
        except Exception as e:
            logger.warning(f"Redis memory read failed for session {session_id}: {e}. Falling back to MongoDB.")
            history_list = []
        
        if not history_list:
            # 2. Rehydrate from MongoDB (Long-Term Memory)
            try:
                docs = await ChatHistoryRepository.get_recent_history(session_id, limit=cls.HISTORY_LIMIT // 2)
                if not docs:
                    return ""
                    
                for doc in docs:
                    msg_str = json.dumps({"role": doc["role"], "content": doc["content"]})
                    history_list.append(msg_str)
                    
                # Rehydrate Redis in the background (fault-tolerant)
                try:
                    for doc in docs:
                        msg_str = json.dumps({"role": doc["role"], "content": doc["content"]})
                        await redis_client.rpush(key, msg_str)
                    await redis_client.expire(key, cls.TTL_SECONDS)
                except Exception as ex:
                    logger.debug(f"Redis rehydration skipped: {ex}")
            except Exception as e:
                logger.error(f"MongoDB history read failed for session {session_id}: {e}")
                return ""
        
        # Format history into a string
        formatted = []
        for item in history_list:
            try:
                msg = json.loads(item)
                role = "User" if msg.get("role") == "user" else "Assistant"
                formatted.append(f"{role}: {msg.get('content', '')}")
            except Exception:
                continue
            
        return "\n".join(formatted)

    @classmethod
    async def save_turn(
        cls, 
        session_id: str, 
        vendor_id: str, 
        question: str, 
        answer: str,
        employee_id: Optional[str] = None
    ):
        key = cls._get_key(session_id)
        now = datetime.now(timezone.utc).isoformat()
        
        q_msg = {"role": "user", "content": question}
        a_msg = {"role": "assistant", "content": answer}
        
        # 1. Save to Redis (Cache, fault-tolerant)
        try:
            await redis_client.rpush(key, json.dumps(q_msg), json.dumps(a_msg))
            await redis_client.ltrim(key, -cls.HISTORY_LIMIT, -1)
            await redis_client.expire(key, cls.TTL_SECONDS)
        except Exception as e:
            logger.warning(f"Redis cache save failed for session {session_id}: {e}")
        
        # 2. Save to MongoDB (Permanent System of Record with optional employee context)
        try:
            await ChatHistoryRepository.append_message(
                session_id,
                vendor_id,
                "user",
                question,
                now,
                employee_id
            )
            await ChatHistoryRepository.append_message(
                session_id,
                vendor_id,
                "assistant",
                answer,
                now,
                employee_id
            )
        except Exception as e:
            logger.error(f"MongoDB message append failed for session {session_id}: {e}")
