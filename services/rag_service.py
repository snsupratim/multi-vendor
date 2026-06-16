from services.retrieval_service import (
    RetrievalService
)

from services.chat_service import (
    ChatService
)
from loguru import logger

class RAGService:

    @staticmethod
    def ask(
        question: str,
        workspace_id: str
    ):
        
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

        answer = (
            ChatService.generate_answer(
                question,
                chunks
            )
        )

        return {
            "answer": answer,
            "sources": len(chunks)
        }