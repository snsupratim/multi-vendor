from groq import AsyncGroq

from core.config import settings

client = AsyncGroq(
    api_key=settings.GROQ_API_KEY
)


class GroqProvider:

    @staticmethod
    async def generate(
        *,
        prompt: str,
        model_name: str
    ):

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response.choices[0].message.content
        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(response, "usage") and response.usage:
            prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

        return {
            "text": text,
            "usage": usage
        }