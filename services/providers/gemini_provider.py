import google.generativeai as genai

from core.config import settings

genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class GeminiProvider:

    @staticmethod
    async def generate(
        *,
        prompt: str,
        model_name: str
    ):
        model = genai.GenerativeModel(
            model_name
        )

        response = await model.generate_content_async(
            prompt
        )

        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

        return {
            "text": response.text,
            "usage": usage
        }