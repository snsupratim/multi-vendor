import google.generativeai as genai

from core.config import settings

genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class GeminiProvider:

    @staticmethod
    def generate(
        *,
        prompt: str,
        model_name: str
    ):

        model = genai.GenerativeModel(
            model_name
        )

        response = model.generate_content(
            prompt
        )

        return response.text