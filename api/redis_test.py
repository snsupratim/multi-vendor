from fastapi import APIRouter

from services.rate_limit_service import redis_client

router = APIRouter()


@router.get("/test-redis")
async def test_redis():

    await redis_client.set(
        "hello",
        "world"
    )

    value = await redis_client.get(
        "hello"
    )

    return {
        "value": value
    }