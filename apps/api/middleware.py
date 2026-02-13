from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("divyadrishti.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)  # type: ignore[misc]
        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "%s %s %d %.1fms",
            request.method, request.url.path,
            response.status_code, elapsed,
        )
        return response
