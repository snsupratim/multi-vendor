import google.generativeai as genai
from core.config import settings
from loguru import logger
import sentry_sdk

genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class EmbeddingService:

    @staticmethod
    def get_embedding(text: str):

        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                output_dimensionality=768
            )

            embedding = result["embedding"]

            if len(embedding) != 768:
                raise ValueError(
                    f"Expected 768 dimensions, got {len(embedding)}"
                )

            return embedding

        except Exception as e:
            logger.exception("Embedding failed")

            sentry_sdk.capture_exception(e)

            raise