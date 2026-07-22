import asyncio
import re
from collections import deque
from repositories.log_repository import LogRepository

# Simple thread-safe and event-loop agnostic queue
log_queue = deque()

def mongo_sink_handler(message):
    """
    Loguru synchronous sink that formats the log record and pushes it to our deque.
    This avoids all asyncio event loop binding issues!
    """
    try:
        record = message.record
        msg_str = record["message"]
        
        workspace_match = re.search(r"workspace=([a-zA-Z0-9-]+)", msg_str)
        vendor_match = re.search(r"vendor=([a-zA-Z0-9-]+)", msg_str)
        session_match = re.search(r"session=([a-zA-Z0-9-]+)", msg_str)
        
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": msg_str,
            "workspace_id": workspace_match.group(1) if workspace_match else None,
            "vendor_id": vendor_match.group(1) if vendor_match else None,
            "session_id": session_match.group(1) if session_match else None
        }
        
        log_queue.append(log_data)
        # Debug print
        print(f"[DEBUG] Appended log to deque. Queue length: {len(log_queue)}")
    except Exception as e:
        print(f"[DEBUG] Failed to extract log: {e}")

async def start_mongo_logger():
    """
    Background worker that continuously reads from the deque and writes to MongoDB.
    """
    print("[DEBUG] Background mongo logger started successfully!")
    while True:
        try:
            if log_queue:
                log_data = log_queue.popleft()
                print(f"[DEBUG] Popped log from deque. Writing to Mongo...")
                await LogRepository.append_log(log_data)
                print(f"[DEBUG] Successfully wrote log to Mongo!")
            else:
                # Sleep briefly if the queue is empty to avoid blocking the event loop
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("[DEBUG] Background logger cancelled.")
            break
        except Exception as e:
            # We print directly to stdout to avoid infinite logging loops if the DB fails
            print(f"[DEBUG] Failed to write log to Mongo: {e}")
            await asyncio.sleep(1) # Prevent tight crash loops
