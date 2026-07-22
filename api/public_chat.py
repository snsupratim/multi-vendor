import time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from core.api_key_dependency import (
    get_api_key_context
)

from schemas.public_chat_schema import (
    PublicChatRequest
)

from services.cost_service import (
    CostService
)

from services.rag_service import (
    RAGService
)

from services.rate_limit_service import (
    RateLimitService
)

from services.token_service import (
    TokenService
)

from services.usage_service import (
    UsageService
)

router = APIRouter(
    prefix="/v1/public",
    tags=["Public Chat"]
)


@router.post("/chat")
async def public_chat(
    payload: PublicChatRequest,
    api_context=Depends(
        get_api_key_context
    )
):

    start = time.perf_counter()

    subscription = api_context["subscription"]

    #
    # Requests per minute
    #

    allowed = await (
        RateLimitService.check_minute_limit(
            api_context["api_key_id"],
            subscription["requests_per_minute"]
        )
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Per-minute request limit exceeded"
        )

    #
    # Requests per hour
    #

    allowed = await (
        RateLimitService.check_hour_limit(
            api_context["api_key_id"],
            subscription["requests_per_hour"]
        )
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Per-hour request limit exceeded"
        )

    #
    # Estimate input tokens
    #

    input_tokens = (
        TokenService.count_tokens(
            payload.question
        )
    )

    current_input = await (
        RateLimitService.get_input_tokens(
            api_context["api_key_id"]
        )
    )

    if (
        current_input + input_tokens
        >
        subscription["input_tokens_per_day"]
    ):
        raise HTTPException(
            status_code=429,
            detail="Input token limit exceeded"
        )

    try:

        #
        # Execute RAG
        #

        import uuid
        session_id = payload.session_id if payload.session_id else str(uuid.uuid4())

        result = await RAGService.ask(
            question=payload.question,
            workspace_id=api_context["workspace_id"],
            model_family=payload.model_family,
            model_name=payload.model_name,
            session_id=session_id
        )

        answer_text = result["answer"]

        output_tokens = (
            TokenService.count_tokens(
                answer_text
            )
        )

        current_output = await (
            RateLimitService.get_output_tokens(
                api_context["api_key_id"]
            )
        )

        if (
            current_output + output_tokens
            >
            subscription["output_tokens_per_day"]
        ):
            raise HTTPException(
                status_code=429,
                detail="Output token limit exceeded"
            )

        #
        # Commit token usage only after success
        #

        await (
            RateLimitService.add_input_tokens(
                api_context["api_key_id"],
                input_tokens
            )
        )

        await (
            RateLimitService.add_output_tokens(
                api_context["api_key_id"],
                output_tokens
            )
        )

        latency_ms = int(
            (
                time.perf_counter()
                - start
            ) * 1000
        )

        estimated_cost = (
            CostService.estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        )

        await UsageService.log_request(
            api_key_id=api_context["api_key_id"],
            vendor_id=api_context["vendor_id"],
            workspace_id=api_context["workspace_id"],
            model_name=payload.model_name,
            endpoint="/v1/public/chat",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
            latency_ms=latency_ms,
            status="SUCCESS"
        )

        return result

    except Exception as ex:

        latency_ms = int(
            (
                time.perf_counter()
                - start
            ) * 1000
        )

        #
        # Log failure only.
        # Do NOT consume token quota.
        #

        await UsageService.log_request(
            api_key_id=api_context["api_key_id"],
            vendor_id=api_context["vendor_id"],
            workspace_id=api_context["workspace_id"],
            model_name=payload.model_name,
            endpoint="/v1/public/chat",
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0,
            latency_ms=latency_ms,
            status="FAILED",
            error_message=str(ex)
        )

        raise