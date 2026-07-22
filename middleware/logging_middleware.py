import time
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.apm import APMService

class APMMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        
        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start) * 1000)
            
            # Record performance
            APMService.capture_performance(
                endpoint=request.url.path,
                method=request.method,
                latency_ms=duration_ms,
                status_code=response.status_code
            )
            
            # Keep standard loguru logging
            logger.info(
                f"{request.method} {request.url.path} "
                f"status={response.status_code} "
                f"time={duration_ms}ms"
            )
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            
            # Automatically capture unhandled exceptions!
            APMService.capture_exception(e, context={
                "endpoint": request.url.path,
                "method": request.method,
                "latency_ms": duration_ms
            })
            
            # Record performance failure
            APMService.capture_performance(
                endpoint=request.url.path,
                method=request.method,
                latency_ms=duration_ms,
                status_code=500
            )
            
            # Return standard 500 error instead of crashing the server
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )