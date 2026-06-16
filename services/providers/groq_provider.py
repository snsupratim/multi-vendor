from groq import Groq

from core.config import settings

client = Groq(
    api_key=settings.GROQ_API_KEY
)


class GroqProvider:

    @staticmethod
    def generate(
        *,
        prompt: str,
        model_name: str
    ):

        response = (
            client.chat.completions.create(

                model=model_name,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )