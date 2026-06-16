from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis

from core.config import settings


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


class RateLimitService:

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _minute_bucket() -> str:
        return RateLimitService._now().strftime(
            "%Y%m%d%H%M"
        )

    @staticmethod
    def _hour_bucket() -> str:
        return RateLimitService._now().strftime(
            "%Y%m%d%H"
        )

    @staticmethod
    def _day_bucket() -> str:
        return RateLimitService._now().strftime(
            "%Y%m%d"
        )

    @staticmethod
    def _seconds_until_next_minute() -> int:
        now = RateLimitService._now()

        next_minute = (
            now.replace(
                second=0,
                microsecond=0
            )
            + timedelta(minutes=1)
        )

        return max(
            1,
            int(
                (next_minute - now).total_seconds()
            )
        )

    @staticmethod
    def _seconds_until_next_hour() -> int:
        now = RateLimitService._now()

        next_hour = (
            now.replace(
                minute=0,
                second=0,
                microsecond=0
            )
            + timedelta(hours=1)
        )

        return max(
            1,
            int(
                (next_hour - now).total_seconds()
            )
        )

    @staticmethod
    def _seconds_until_next_day() -> int:
        now = RateLimitService._now()

        next_day = (
            now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            + timedelta(days=1)
        )

        return max(
            1,
            int(
                (next_day - now).total_seconds()
            )
        )

    @staticmethod
    async def check_minute_limit(
        api_key_id: str,
        limit: int
    ) -> bool:

        key = (
            f"rate:min:{api_key_id}:"
            f"{RateLimitService._minute_bucket()}"
        )

        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(
                key,
                RateLimitService._seconds_until_next_minute()
            )

        return current <= limit

    @staticmethod
    async def check_hour_limit(
        api_key_id: str,
        limit: int
    ) -> bool:

        key = (
            f"rate:hour:{api_key_id}:"
            f"{RateLimitService._hour_bucket()}"
        )

        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(
                key,
                RateLimitService._seconds_until_next_hour()
            )

        return current <= limit

    @staticmethod
    async def add_input_tokens(
        api_key_id: str,
        tokens: int
    ) -> int:

        key = (
            f"tokens:input:{api_key_id}:"
            f"{RateLimitService._day_bucket()}"
        )

        current = await redis_client.incrby(
            key,
            tokens
        )

        if current == tokens:
            await redis_client.expire(
                key,
                RateLimitService._seconds_until_next_day()
            )

        return current

    @staticmethod
    async def add_output_tokens(
        api_key_id: str,
        tokens: int
    ) -> int:

        key = (
            f"tokens:output:{api_key_id}:"
            f"{RateLimitService._day_bucket()}"
        )

        current = await redis_client.incrby(
            key,
            tokens
        )

        if current == tokens:
            await redis_client.expire(
                key,
                RateLimitService._seconds_until_next_day()
            )

        return current

    @staticmethod
    async def get_input_tokens(
        api_key_id: str
    ) -> int:

        key = (
            f"tokens:input:{api_key_id}:"
            f"{RateLimitService._day_bucket()}"
        )

        value = await redis_client.get(key)

        return int(value or 0)

    @staticmethod
    async def get_output_tokens(
        api_key_id: str
    ) -> int:

        key = (
            f"tokens:output:{api_key_id}:"
            f"{RateLimitService._day_bucket()}"
        )

        value = await redis_client.get(key)

        return int(value or 0)