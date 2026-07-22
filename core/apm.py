import asyncio
import traceback
from collections import deque
from datetime import datetime, timezone
from repositories.apm_repository import APMRepository
from loguru import logger

# Thread-safe and event-loop agnostic deque
apm_queue = deque()

class APMService:
    @staticmethod
    def capture_exception(e: Exception, context: dict = None):
        """
        Manually capture an exception, extract its traceback, and queue it for MongoDB.
        """
        tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        
        error_data = {
            "type": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "stack_trace": tb_str,
            "context": context or {}
        }
        
        apm_queue.append(error_data)
        logger.error(f"APM captured exception: {str(e)}")

    @staticmethod
    def capture_performance(endpoint: str, method: str, latency_ms: int, status_code: int):
        """
        Queue a performance metric for MongoDB.
        """
        perf_data = {
            "type": "performance",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "method": method,
            "latency_ms": latency_ms,
            "status_code": status_code
        }
        
        apm_queue.append(perf_data)

async def start_apm_worker():
    """
    Background worker that continuously reads from the APM deque and writes to MongoDB.
    """
    print("[DEBUG] Background APM worker started successfully!")
    while True:
        try:
            if apm_queue:
                data = apm_queue.popleft()
                if data["type"] == "error":
                    await APMRepository.append_error(data)
                elif data["type"] == "performance":
                    await APMRepository.append_performance(data)
            else:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("[DEBUG] Background APM worker cancelled.")
            break
        except Exception as e:
            print(f"[DEBUG] Failed to write APM data to Mongo: {e}")
            await asyncio.sleep(1)
