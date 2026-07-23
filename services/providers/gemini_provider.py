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

        return response.text