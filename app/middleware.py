import uuid
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
from starlette.responses import JSONResponse

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
     request_id = uuid.uuid4()
     start = time.time()
     content_length = request.headers.get("content-length")
     if content_length and int(content_length) > 1_000_000:
      return JSONResponse(413, "Слишком большой запрос")
     response = await call_next(request)
     response.headers["X-Request-ID"] = str(request_id)
     response.headers.update({"server" : "My-hotel"})
     duration = time.time() - start
     logger.info(f"[{str(request_id)}] {request.method} {request.url.path} ->"
                 f" {response.status_code} {duration:.3f}s")
     return response


