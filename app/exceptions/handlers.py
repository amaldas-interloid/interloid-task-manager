import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, AppException):
        return await generic_exception_handler(request, exc)

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": {
                "code": exc.code,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        return await generic_exception_handler(request, exc)

    details: dict[str, list[str]] = {}

    for error in exc.errors():
        location = error.get("loc", [])

        # Remove "body", "query", "path", etc.
        field = str(location[-1]) if location else "request"

        message = str(error.get("msg", "Invalid value"))

        details.setdefault(field, []).append(message)

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "details": details,
            },
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "details": None,
            },
        },
    )


async def http_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        return await generic_exception_handler(request, exc)

    code_by_status = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None,
            "error": {
                "code": code_by_status.get(
                    exc.status_code,
                    "HTTP_ERROR",
                ),
                "details": None,
            },
        },
        headers=exc.headers,
    )
