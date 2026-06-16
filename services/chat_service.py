import google.generativeai as genai

from core.config import settings

from loguru import logger
import sentry_sdk
from services.model_router import (
    ModelRouter
)

genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


class ChatService:

    @staticmethod
    def generate_answer(
        question: str,
        contexts: list,
        model_name: str = "gemini-2.5-flash"
    ):

        try:
            context_text = "\n\n".join(
                [
                    c["content"]
                    for c in contexts
                ]
            )

            prompt = f"""
You are a helpful assistant.

Use ONLY the provided context.

Context:
{context_text}

Question:
{question}

Answer:
"""

            answer = ModelRouter.generate(
            prompt=prompt,
            model_name=model_name
            )
            

            return answer

        except Exception as e:

            logger.exception(
                "generation failed"
            )

            sentry_sdk.capture_exception(
                e
            )

            raise