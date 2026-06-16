import uuid

from datetime import (
    datetime,
    timezone
)

from repositories.usage_repository import (
    UsageRepository
)


class UsageService:

    @staticmethod
    async def log_request(
        *,
        api_key_id: str,
        vendor_id: str,
        workspace_id: str,
        model_name: str,
        endpoint: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd: float,
        latency_ms: int,
        status: str,
        error_message: str | None = None
    ):

        await UsageRepository.create(
            {
                "request_id": str(
                    uuid.uuid4()
                ),

                "api_key_id": api_key_id,

                "vendor_id": vendor_id,

                "workspace_id": workspace_id,
                "model": model_name,

                "endpoint": endpoint,

                "input_tokens": input_tokens,

                "output_tokens": output_tokens,

                "estimated_cost_usd": estimated_cost_usd,

                "latency_ms": latency_ms,

                "status": status,

                "error_message": error_message,

                "created_at": datetime.now(
                    timezone.utc
                )
            }
        )