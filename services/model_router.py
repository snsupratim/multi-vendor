from services.providers.gemini_provider import (
    GeminiProvider
)

from services.providers.groq_provider import (
    GroqProvider
)

from repositories.model_repository import (
    ModelRepository
)


class ModelRouter:

    @staticmethod
    async def generate(
        *,
        prompt: str,
        model_family: str,
        model_name: str
    ):

        model = await ModelRepository.get_by_name_and_family(
            model_name,
            model_family
        )

        if not model:
            raise ValueError(
                f"Unsupported model: {model_name} in family {model_family}"
            )

        provider = model.get("provider", "").lower()
        family = model_family.lower()

        if provider == "google" or family == "gemini":
            return await GeminiProvider.generate(
                prompt=prompt,
                model_name=model_name
            )

        if provider == "groq" or family in ["llama", "groq", "openai"]:
            return await GroqProvider.generate(
                prompt=prompt,
                model_name=model_name
            )

        raise ValueError(
            f"Unknown provider or family routing for provider='{provider}', family='{family}'"
        )