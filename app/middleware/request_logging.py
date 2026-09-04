import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.info(
            "request_id=%s | %s %s - %d",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
        )

        return response
