from google.api_core.exceptions import (
    ResourceExhausted
)

from loguru import logger

from services.chat_service import (
    ChatService
)

from services.retrieval_service import (
    RetrievalService
)

from repositories.workspace_repository import WorkspaceRepository


from services.memory_service import MemoryService

class RAGService:

    @staticmethod
    async def ask(
        question: str,
        workspace_id: str,
        model_family: str,
        model_name: str,
        session_id: str
    ):

        try:
            workspace = await WorkspaceRepository.get_by_workspace_id(workspace_id)
            vendor_id = workspace.get("vendor_id") if workspace else None
            system_prompt = workspace.get("system_prompt") if workspace else None

            logger.info(
                f"Question received "
                f"workspace={workspace_id} "
                f"session={session_id} "
                f"vendor={vendor_id}"
            )

            chunks = (
                RetrievalService.retrieve(
                    question,
                    workspace_id
                )
            )

            logger.info(
                f"Retrieved "
                f"{len(chunks)} chunks "
                f"workspace={workspace_id} "
                f"session={session_id} "
                f"vendor={vendor_id}"
            )

            history = await MemoryService.get_history(session_id)

            gen_result = await ChatService.generate_answer(
                question,
                chunks,
                model_family=model_family,
                model_name=model_name,
                system_prompt=system_prompt,
                history=history
            )

            answer = gen_result.get("text", "") if isinstance(gen_result, dict) else str(gen_result)
            usage = gen_result.get("usage", {}) if isinstance(gen_result, dict) else {}

            # Log token usage & update vendor billing
            if usage and vendor_id:
                from services.billing_service import BillingService
                await BillingService.log_usage(
                    vendor_id=vendor_id,
                    session_id=session_id,
                    model_name=model_name or "gemini-2.5-flash",
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0)
                )

            await MemoryService.save_turn(session_id, vendor_id, question, answer)

            return {
                "answer": answer,
                "sources": len(chunks),
                "session_id": session_id,
                "usage": usage
            }

        except ResourceExhausted as ex:

            logger.warning(
                f"Gemini quota exceeded "
                f"workspace={workspace_id} "
                f"error={str(ex)}"
            )

            # Re-raise so the API layer can convert it to HTTP 429
            raise

        except Exception:

            logger.exception(
                f"RAG pipeline failed "
                f"workspace={workspace_id}"
            )

            raise