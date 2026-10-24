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
        conn = await asyncpg.connect(settings.PAYROLL_DB_URL, timeout=10)
        version = await conn.fetchval('SELECT version()')
        await conn.close()
        # Do not log the password
        safe_url = settings.PAYROLL_DB_URL.replace(settings.PAYROLL_DB_URL.split(":")[2].split("@")[0], "HIDDEN_PASSWORD")
        return {"status": "success", "version": version, "url_used": safe_url}
    except Exception as e:
        safe_url = settings.PAYROLL_DB_URL.replace(settings.PAYROLL_DB_URL.split(":")[2].split("@")[0], "HIDDEN_PASSWORD")
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
    
    # 1. Verify Access (Temporarily bypassed: Open access for all vendors)
    # has_access = await VendorAccessRepository.check_access(vendor_id, module_id)
    # if not has_access:
    #     raise HTTPException(
    #         status_code=403,
    #         detail=f"Vendor {vendor_id} does not have access to Module {module_id}"
    #     )
        
    try:
        from services.memory_service import MemoryService
        from repositories.module_repository import ModuleRepository
        from services.sql_agent.agent_tools import retrieve_business_context
        from services.billing_service import BillingService
        
        # 2. Fetch Conversation History
        history_text = await MemoryService.get_history(session_id)
        
        # 3. Fetch Module Data (for dynamic system prompt)
        module_doc = await ModuleRepository.get_by_module_id(module_id)
        module_system_prompt = module_doc.get("system_prompt", "") if module_doc else ""
        
        # 4. Fetch Business Context (RAG for business logic)
        business_context = retrieve_business_context.invoke({"query": payload.question})
        
        # 5. Trigger the LangGraph Agent
        logger.info(f"Triggering Analytics Agent for Vendor: {vendor_id} | Module: {module_id}")
        
        agent_workflow = SQLAgentWorkflow(
            model_family=payload.model_family,
            model_name=payload.model_name
        )
        result = await agent_workflow.run(
            question=payload.question,
            vendor_id=vendor_id,
            module_id=module_id,
            history=history_text,
            module_system_prompt=module_system_prompt,
            business_context=business_context,
            user_context=payload.user_context
        )
        
        # 6. Log Token Usage
        usage = result.get("usage", {})
        if usage:
            await BillingService.log_usage(
                vendor_id=vendor_id,
                session_id=session_id,
                model_name=payload.model_name or "default",
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0)
            )
        
        # We attempt to parse the raw markdown output into a clean JSON dict 
        # so the frontend can immediately consume it for charting.
        raw_response = result.get("raw_response", "")
        
        # Extract employee_id from user_context if provided
        employee_id = None
        if isinstance(payload.user_context, dict):
            employee_id = payload.user_context.get("employee_id") or payload.user_context.get("user_id")

        # Save to Hot/Cold Memory
        await MemoryService.save_turn(
            session_id=session_id, 
            vendor_id=vendor_id, 
            question=payload.question, 
            answer=raw_response,
            employee_id=employee_id
        )
        
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
            if "components" not in structured_data:
                # If LLM still returned old format, wrap it
                structured_data = {"components": [structured_data], "suggestions": []}
            if "suggestions" not in structured_data:
                structured_data["suggestions"] = []
        except json.JSONDecodeError:
            # Fallback if the LLM outputted conversational text instead of raw JSON
            structured_data = {
                "components": [
                    {
                        "componentType": "TEXT",
                        "title": "Analytics Response",
                        "description": raw_response,
                        "config": {},
                        "data": []
                    }
                ],
                "suggestions": []
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
            "components": [
                {
                    "componentType": "TEXT",
                    "title": "Analytics Error",
                    "description": f"The analytics engine encountered an unexpected error: {str(e)}",
                    "config": {},
                    "data": []
                }
            ],
            "session_id": session_id if 'session_id' in locals() else ""
        }
