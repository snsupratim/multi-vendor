import google.generativeai as genai

from core.config import settings

from loguru import logger
import sentry_sdk

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
        contexts: list
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

            response = model.generate_content(
                prompt
            )
            

            return response.text

        except Exception as e:

            logger.exception(
                "Gemini generation failed"
            )

            sentry_sdk.capture_exception(
                e
            )

            raise