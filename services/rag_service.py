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


class RAGService:

    @staticmethod
    async def ask(
        question: str,
        workspace_id: str,
        model_name: str
    ):

        try:

            logger.info(
                f"Question received "
                f"workspace={workspace_id}"
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
                f"workspace={workspace_id}"
            )

            answer = ChatService.generate_answer(
                    question,
                    chunks,
                    model_name=model_name
                )
        

            return {
                "answer": answer,
                "sources": len(chunks)
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