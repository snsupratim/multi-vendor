from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from repositories.chat_history_repository import ChatHistoryRepository
from core.apm import APMService
from loguru import logger

router = APIRouter(prefix="/history", tags=["Chat History"])

@router.get("/sessions/{vendor_id}")
async def get_all_sessions(
    vendor_id: str,
    employee_id: Optional[str] = Query(None, description="Optional employee ID to filter sessions within a vendor")
):
    """
    Fetches all unique chat sessions for a specific vendor.
    Optionally filter by employee_id: /history/sessions/{vendor_id}?employee_id={employee_id}
    """
    try:
        sessions = await ChatHistoryRepository.get_sessions(vendor_id, employee_id=employee_id)
        return {
            "vendor_id": vendor_id,
            "employee_id": employee_id,
            "sessions": sessions
        }
    except Exception as e:
        logger.exception("Failed to fetch sessions")
        APMService.capture_exception(e, context={"vendor_id": vendor_id, "employee_id": employee_id, "type": "get_sessions"})
        raise HTTPException(status_code=500, detail="Failed to fetch chat history sessions")

@router.get("/sessions/{vendor_id}/{employee_id}")
async def get_employee_sessions(vendor_id: str, employee_id: str):
    """
    Fetches all unique chat sessions for a specific employee under a specific vendor.
    Used to view an employee's chat session history.
    """
    try:
        sessions = await ChatHistoryRepository.get_sessions(vendor_id=vendor_id, employee_id=employee_id)
        return {
            "vendor_id": vendor_id,
            "employee_id": employee_id,
            "sessions": sessions
        }
    except Exception as e:
        logger.exception("Failed to fetch employee sessions")
        APMService.capture_exception(e, context={"vendor_id": vendor_id, "employee_id": employee_id, "type": "get_employee_sessions"})
        raise HTTPException(status_code=500, detail="Failed to fetch employee chat history sessions")

@router.get("/session/{session_id}")
async def get_session_messages(session_id: str):
    """
    Fetches all messages in chronological order for a specific chat session.
    Used to reload a past conversation in the main chat window.
    """
    try:
        messages = await ChatHistoryRepository.get_session_messages(session_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch session messages")
        APMService.capture_exception(e, context={"session_id": session_id, "type": "get_session_messages"})
        raise HTTPException(status_code=500, detail="Failed to fetch session messages")
