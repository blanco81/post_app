import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("Timing")
logging.basicConfig(level=logging.INFO)

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()  
        response = await call_next(request)  
        end_time = time.perf_counter() 
        process_time = end_time - start_time  
        logger.info(f" Request: {request.method} {request.url} - Duration: {process_time:.4f} seconds")

        return response
