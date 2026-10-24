from fastapi import HTTPException
from loguru import logger
from repositories.vendor_access_repository import VendorAccessRepository
from repositories.module_repository import ModuleRepository
from services.retrieval_service import RetrievalService
from services.chat_service import ChatService
from services.memory_service import MemoryService
from google.api_core.exceptions import ResourceExhausted

class ModuleRAGService:
    @staticmethod
    async def ask(
        question: str, 
        module_id: str, 
        vendor_id: str, 
        model_family: str, 
        model_name: str, 
        session_id: str,
        user_context: dict = None
    ):
        try:
            # 1. Authorize (Temporarily bypassed: Open access for all vendors)
            # has_access = await VendorAccessRepository.check_access(vendor_id, module_id)
            # if not has_access:
            #     raise HTTPException(status_code=403, detail="Vendor does not have access to this module")
            
            # 2. Fetch module
            module_doc = await ModuleRepository.get_by_module_id(module_id)
            if not module_doc:
                raise HTTPException(status_code=404, detail="Module not found")
                
            system_prompt = module_doc.get("system_prompt")
            
            logger.info(f"Module Question received workspace={module_id} session={session_id} vendor={vendor_id}")
            
            # 3. Retrieve chunks (We reuse the workspace_id in supabase as module_id)
            chunks = RetrievalService.retrieve(question, module_id)
            
            logger.info(f"Retrieved {len(chunks)} chunks workspace={module_id} session={session_id} vendor={vendor_id}")
            
            # 4. Memory
            history = await MemoryService.get_history(session_id)
            
            # 5. Generate
            gen_result = await ChatService.generate_answer(
                question, 
                chunks, 
                model_family=model_family, 
                model_name=model_name, 
                system_prompt=system_prompt, 
                history=history,
                user_context=user_context
            )

            answer = gen_result.get("text", "") if isinstance(gen_result, dict) else str(gen_result)
            usage = gen_result.get("usage", {}) if isinstance(gen_result, dict) else {}
            
            # 6. Log Token Usage & Vendor Billing
            if usage:
                from services.billing_service import BillingService
                await BillingService.log_usage(
                    vendor_id=vendor_id,
                    session_id=session_id,
                    model_name=model_name or "gemini-2.5-flash",
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0)
                )
            
            # Extract employee_id from user_context if provided
            employee_id = None
            if isinstance(user_context, dict):
                employee_id = user_context.get("employee_id") or user_context.get("user_id")

            # Save to Hot/Cold Memory
            await MemoryService.save_turn(
                session_id=session_id, 
                vendor_id=vendor_id, 
                question=question, 
                answer=answer,
                employee_id=employee_id
            )
            
            return {
                "answer": answer,
                "sources": len(chunks),
                "session_id": session_id,
                "usage": usage
            }
            
        except HTTPException:
            raise
        except ResourceExhausted as ex:
            logger.warning(f"Gemini quota exceeded workspace={module_id} error={str(ex)}")
            raise
        except Exception:
            logger.exception(f"Module RAG pipeline failed workspace={module_id}")
            raise
