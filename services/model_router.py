from services.model_registry import (
    SUPPORTED_MODELS
)

from services.providers.gemini_provider import (
    GeminiProvider
)

from services.providers.groq_provider import (
    GroqProvider
)


class ModelRouter:

    @staticmethod
    def generate(
        *,
        prompt: str,
        model_name: str
    ):

        if model_name not in SUPPORTED_MODELS:

            raise ValueError(
                f"Unsupported model: {model_name}"
            )

        provider = (
            SUPPORTED_MODELS[
                model_name
            ]["provider"]
        )

        if provider == "gemini":

            return (
                GeminiProvider.generate(
                    prompt=prompt,
                    model_name=model_name
                )
            )

        if provider == "groq":

            return (
                GroqProvider.generate(
                    prompt=prompt,
                    model_name=model_name
                )
            )

        raise ValueError(
            "Unknown provider"
        )