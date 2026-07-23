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

        return (
            response
            .choices[0]
            .message
            .content
        )