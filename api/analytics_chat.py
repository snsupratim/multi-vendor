from fastapi import APIRouter, HTTPException
from schemas.module_schema import ModuleChatRequest
from repositories.vendor_access_repository import VendorAccessRepository
from services.sql_agent.agent_workflow import SQLAgentWorkflow
from core.apm import APMService
from loguru import logger
import json

router = APIRouter(prefix="/analytics-chat", tags=["Module Analytics (Text-to-SQL)"])

@router.get("/db-test")
async def test_db_connection():
    try:
        from core.config import settings
        import asyncpg
        conn = await asyncpg.connect(settings.SUPABASE_DB_URL, timeout=10)
        version = await conn.fetchval('SELECT version()')
        await conn.close()
        # Do not log the password
        safe_url = settings.SUPABASE_DB_URL.replace(settings.SUPABASE_DB_URL.split(":")[2].split("@")[0], "HIDDEN_PASSWORD")
        return {"status": "success", "version": version, "url_used": safe_url}
    except Exception as e:
        safe_url = settings.SUPABASE_DB_URL.replace(settings.SUPABASE_DB_URL.split(":")[2].split("@")[0], "HIDDEN_PASSWORD")
        return {"status": "error", "type": type(e).__name__, "message": str(e), "url_used": safe_url}

@router.post("")
async def analytics_module_chat(payload: ModuleChatRequest):
    """
    Executes a Text-to-SQL query using the LangGraph Agent.
    This bypasses JWT and expects standard proprietary software integration 
    where the vendor_id is explicitly passed.
    """
    import uuid
    vendor_id = payload.vendor_id
    module_id = payload.module_id
    session_id = payload.session_id or str(uuid.uuid4())
    
    # 1. Verify Access
    has_access = await VendorAccessRepository.check_access(vendor_id, module_id)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail=f"Vendor {vendor_id} does not have access to Module {module_id}"
        )
        
    try:
        from services.memory_service import MemoryService
        
        # 2. Fetch Conversation History
        history_text = await MemoryService.get_history(session_id)
        
        # 3. Trigger the LangGraph Agent
        logger.info(f"Triggering Analytics Agent for Vendor: {vendor_id} | Module: {module_id}")
        
        agent_workflow = SQLAgentWorkflow(
            model_family=payload.model_family,
            model_name=payload.model_name
        )
        result = await agent_workflow.run(
            question=payload.question,
            vendor_id=vendor_id,
            module_id=module_id,
            history=history_text
        )
        
        # We attempt to parse the raw markdown output into a clean JSON dict 
        # so the frontend can immediately consume it for charting.
        raw_response = result.get("raw_response", "")
        
        # Save to Hot/Cold Memory
        await MemoryService.save_turn(session_id, payload.question, raw_response)
        
        # If the LLM returns a list (e.g. [{"text": "..."}]), extract the text
        if isinstance(raw_response, list):
            # Attempt to extract text from the first part, or stringify it
            extracted = ""
            for part in raw_response:
                if isinstance(part, dict) and "text" in part:
                    extracted += part["text"]
                elif isinstance(part, str):
                    extracted += part
            raw_response = extracted if extracted else str(raw_response)
        
        if not isinstance(raw_response, str):
            raw_response = str(raw_response)
            
        # Clean up markdown code blocks if the LLM wrapped the JSON in ```json ... ```
        if "```json" in raw_response:
            raw_response = raw_response.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_response:
            raw_response = raw_response.split("```")[1].strip()
            
        try:
            structured_data = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback if the LLM outputted conversational text instead of raw JSON
            structured_data = {
                "componentType": "TEXT",
                "title": "Analytics Response",
                "description": raw_response,
                "config": {},
                "data": []
            }
            
        # Attach the session_id so the frontend can send it back for conversational memory
        structured_data["session_id"] = session_id
            
        return structured_data

    except Exception as e:
        logger.exception("Analytics Agent Failed")
        APMService.capture_exception(
            e,
            context={"module_id": module_id, "vendor_id": vendor_id, "type": "analytics_chat"}
        )
        return {
            "componentType": "TEXT",
            "title": "Analytics Error",
            "description": f"The analytics engine encountered an unexpected error: {str(e)}",
            "config": {},
            "data": []
        }
