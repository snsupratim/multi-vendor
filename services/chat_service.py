import google.generativeai as genai

from core.config import settings

from loguru import logger
from core.apm import APMService
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
    async def generate_answer(
        question: str,
        contexts: list,
        model_family: str = "gemini",
        model_name: str = "gemini-2.5-flash",
        system_prompt: str = None,
        history: str = None,
        user_context: dict = None
    ):

        try:
            context_text = "\n\n".join(
                [
                    c["content"]
                    for c in contexts
                ]
            )
            
            sys_msg = system_prompt if system_prompt else "You are a helpful assistant."
            
            history_section = f"\nConversation History:\n{history}\n" if history else ""

            user_context_section = ""
            if user_context and isinstance(user_context, dict):
                import json
                user_context_section = f"\nUser / Caller Context:\n{json.dumps(user_context, indent=2)}\n"

            prompt = f"""
{sys_msg}
{user_context_section}
Use ONLY the provided context.

Context:
{context_text}
{history_section}
Question:
{question}

Answer:
"""

            result = await ModelRouter.generate(
                prompt=prompt,
                model_family=model_family,
                model_name=model_name
            )

            return result

        except Exception as e:

            logger.exception(
                "generation failed"
            )

            APMService.capture_exception(
                e,
                context={"model_name": model_name, "model_family": model_family}
            )

            raise