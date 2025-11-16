"""
Exception handlers and middleware for global error handling in AurumAI.
Provides consistent error responses across all endpoints.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from models_errors import (
    ApplicationError,
    ErrorCode,
    ErrorResponse,
)

# Configure JSON logger
logger = logging.getLogger("aurumai")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID to each request for tracing.
    Stores request_id in request.state for use in exception handlers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request state."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses.
    Logs errors with structured JSON format.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request/response with error handling."""
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            response = await call_next(request)
            # Log responses with error status codes
            if response.status_code >= 400:
                logger.warning(
                    json.dumps(
                        {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "level": "WARNING",
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": response.status_code,
                            "message": f"HTTP {response.status_code}",
                        }
                    )
                )
        except Exception as exc:
            # Log unhandled exceptions
            logger.error(
                json.dumps(
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "level": "ERROR",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                        "message": "Unhandled exception in request",
                    }
                )
            )
            raise
        else:
            return response


async def application_error_handler(request: Request, exc: Any) -> JSONResponse:
    """
    Handle ApplicationError exceptions.
    Converts ApplicationError to ErrorResponse with proper HTTP status.
    """
    request_id = getattr(request.state, "request_id", None)
    app_error: ApplicationError = exc
    error_response = app_error.to_error_response(request_id)

    logger.warning(
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "WARNING",
                "request_id": request_id,
                "error_code": error_response.error_code,
                "status_code": error_response.status_code,
                "message": error_response.message,
            }
        )
    )

    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.dict(),
    )


async def validation_error_handler(request: Request, exc: Any) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    Converts validation errors to ErrorResponse.
    """
    request_id = getattr(request.state, "request_id", None)
    validation_error: RequestValidationError = exc

    error_details = []
    for error in validation_error.errors():
        loc = ".".join(str(location_part) for location_part in error["loc"][1:])
        error_details.append(
            {
                "field": loc,
                "constraint": error["type"],
                "provided_value": error.get("input", ""),
                "expected_format": error.get("msg", "Invalid value"),
            }
        )

    error_response = ErrorResponse(
        status_code=400,
        error_code=ErrorCode.VALIDATION_ERROR,
        message=f"Validation failed: {len(error_details)} error(s)",
        details=None,
        request_id=request_id,
    )

    logger.warning(
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "WARNING",
                "request_id": request_id,
                "error_code": ErrorCode.VALIDATION_ERROR,
                "status_code": 400,
                "message": "Validation failed",
                "errors": error_details,
            }
        )
    )

    return JSONResponse(
        status_code=400,
        content=error_response.dict(),
    )


async def general_exception_handler(request: Request, exc: Any) -> JSONResponse:
    """
    Handle all other exceptions.
    Converts any unhandled exception to ErrorResponse with 500 status.
    """
    request_id = getattr(request.state, "request_id", None)

    # Don't leak internal error details in production
    error_response = ErrorResponse(
        status_code=500,
        error_code=ErrorCode.INTERNAL_ERROR,
        message="An internal error occurred. Please try again later.",
        details=None,
        request_id=request_id,
    )

    logger.error(
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "ERROR",
                "request_id": request_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "error_code": ErrorCode.INTERNAL_ERROR,
                "status_code": 500,
                "message": "Unhandled exception",
            }
        )
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict(),
    )
