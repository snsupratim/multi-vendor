import time

from loguru import logger

from starlette.middleware.base import (
    BaseHTTPMiddleware
)


class LoggingMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request,
        call_next
    ):

        start = time.time()

        response = await call_next(
            request
        )

        duration = (
            time.time() - start
        )

        logger.info(
            f"{request.method} "
            f"{request.url.path} "
            f"status={response.status_code} "
            f"time={duration:.2f}s"
        )

        return response