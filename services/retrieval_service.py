from db.supabase import supabase
from services.embedding_service import EmbeddingService

from loguru import logger
import sentry_sdk


class RetrievalService:

    @staticmethod
    def retrieve(
        question: str,
        workspace_id: str,
        top_k: int = 5
    ):

        try:
            embedding = EmbeddingService.get_embedding(
                question
            )

            response = (
                supabase.rpc(
                    "match_documents",
                    {
                        "query_embedding": embedding,
                        "p_workspace_id": workspace_id,
                        "match_count": top_k
                    }
                ).execute()
            )


            logger.info(
            f"Retrieval "
            f"workspace={workspace_id} "
            f"chunks={len(response.data)}"
        )
            return response.data

        except Exception as e:
            logger.exception(
                "Vector search failed"
            )

            sentry_sdk.capture_exception(
                e
            )

            raise