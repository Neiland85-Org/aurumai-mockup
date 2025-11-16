"""
Error models and response schemas for AurumAI Backend.
Provides typed, consistent error responses across all endpoints.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional

import json
from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Standardized error codes for all backend errors."""

    # Validation errors (400)
    VALIDATION_ERROR = "validation_error"
    INVALID_MACHINE_ID = "invalid_machine_id"
    INVALID_INPUT = "invalid_input"
    MISSING_REQUIRED_FIELD = "missing_required_field"

    # Resource not found (404)
    NOT_FOUND = "not_found"
    MACHINE_NOT_FOUND = "machine_not_found"
    PREDICTION_NOT_FOUND = "prediction_not_found"
    ESG_DATA_NOT_FOUND = "esg_data_not_found"
    HISTORY_NOT_FOUND = "history_not_found"

    # Authentication/Authorization (401/403)
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"

    # Rate limiting (429)
    RATE_LIMITED = "rate_limited"
    TOO_MANY_REQUESTS = "too_many_requests"

    # Internal server errors (500)
    INTERNAL_ERROR = "internal_error"
    DATABASE_ERROR = "database_error"
    COMPUTATION_ERROR = "computation_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    EXTERNAL_SERVICE_ERROR = "external_service_error"

    # ML/Prediction errors
    MODEL_ERROR = "model_error"
    MODEL_NOT_READY = "model_not_ready"
    PREDICTION_FAILED = "prediction_failed"

    # Ingestion errors
    INGEST_ERROR = "ingest_error"
    INVALID_TELEMETRY = "invalid_telemetry"
    INVALID_FEATURES = "invalid_features"

    # ESG calculation errors
    ESG_CALCULATION_ERROR = "esg_calculation_error"
    INSUFFICIENT_DATA = "insufficient_data"


class HTTPStatusCode(int, Enum):
    """HTTP status codes for error responses."""

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    RATE_LIMITED = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# Mapping from ErrorCode to HTTPStatusCode
ERROR_CODE_TO_STATUS: dict[ErrorCode, HTTPStatusCode] = {
    # 400 errors
    ErrorCode.VALIDATION_ERROR: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.INVALID_MACHINE_ID: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.INVALID_INPUT: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.MISSING_REQUIRED_FIELD: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.INVALID_TELEMETRY: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.INVALID_FEATURES: HTTPStatusCode.BAD_REQUEST,
    # 401 errors
    ErrorCode.UNAUTHORIZED: HTTPStatusCode.UNAUTHORIZED,
    # 403 errors
    ErrorCode.FORBIDDEN: HTTPStatusCode.FORBIDDEN,
    # 404 errors
    ErrorCode.NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.MACHINE_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.PREDICTION_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.ESG_DATA_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.HISTORY_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    # 429 errors
    ErrorCode.RATE_LIMITED: HTTPStatusCode.RATE_LIMITED,
    ErrorCode.TOO_MANY_REQUESTS: HTTPStatusCode.RATE_LIMITED,
    # 500 errors
    ErrorCode.INTERNAL_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.DATABASE_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.COMPUTATION_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.MODEL_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.MODEL_NOT_READY: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.PREDICTION_FAILED: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.INGEST_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.ESG_CALCULATION_ERROR: HTTPStatusCode.INTERNAL_ERROR,
    ErrorCode.INSUFFICIENT_DATA: HTTPStatusCode.INTERNAL_ERROR,
    # 503 errors
    ErrorCode.SERVICE_UNAVAILABLE: HTTPStatusCode.SERVICE_UNAVAILABLE,
    ErrorCode.EXTERNAL_SERVICE_ERROR: HTTPStatusCode.SERVICE_UNAVAILABLE,
}


class ErrorDetails(BaseModel):
    """Optional detailed error information."""

    field: Optional[str] = Field(default=None, description="Field that caused the error")
    constraint: Optional[str] = Field(default=None, description="Constraint that was violated")
    provided_value: Any = Field(default=None, description="Value that was provided")
    expected_format: Optional[str] = Field(default=None, description="Expected format for the field")


class ErrorResponse(BaseModel):
    """
    Standardized error response model.
    Used consistently across all endpoints.
    """

    status_code: int = Field(..., description="HTTP status code", ge=400, le=599)
    error_code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[ErrorDetails] = Field(None, description="Optional detailed error information")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Error occurrence timestamp"
    )
    request_id: Optional[str] = Field(None, description="Request ID for tracing")

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "status_code": 404,
                "error_code": "machine_not_found",
                "message": "Machine with ID 'machine_123' not found in database",
                "details": {
                    "field": "machine_id",
                    "provided_value": "machine_123",
                },
                "timestamp": "2025-11-15T12:34:56Z",
                "request_id": "req_abc123",
            }
        }

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Override dict to ensure timestamp is ISO format."""
        data = super().dict(**kwargs)
        data["timestamp"] = self.timestamp.isoformat() + "Z"
        return data

    def json(self, **kwargs: Any) -> str:
        """Override json to ensure timestamp is ISO format."""
        data = self.dict()
        return json.dumps(data, default=str, **kwargs)


class ValidationError(BaseModel):
    """Validation error response for invalid input."""

    status_code: int = Field(400, description="HTTP status code")
    error_code: ErrorCode = Field(ErrorCode.VALIDATION_ERROR, description="Error code")
    message: str = Field("Validation failed", description="Error message")
    errors: List[ErrorDetails] = Field(
        default_factory=list, description="List of validation errors"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Error timestamp")

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "status_code": 400,
                "error_code": "validation_error",
                "message": "Validation failed",
                "errors": [
                    {
                        "field": "machine_id",
                        "constraint": "length",
                        "provided_value": "",
                        "expected_format": "Non-empty string",
                    }
                ],
                "timestamp": "2025-11-15T12:34:56Z",
            }
        }


class ApplicationError(Exception):
    """
    Base exception class for application errors.
    Maps to ErrorResponse for consistent API responses.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: Optional[int] = None,
        details: Optional[ErrorDetails] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code or ERROR_CODE_TO_STATUS.get(
            error_code, HTTPStatusCode.INTERNAL_ERROR
        )
        self.details = details
        super().__init__(message)

    def to_error_response(self, request_id: Optional[str] = None) -> ErrorResponse:
        """Convert to ErrorResponse for API response."""
        return ErrorResponse(
            status_code=self.status_code,
            error_code=self.error_code,
            message=self.message,
            details=self.details,
            request_id=request_id,
        )


class ValidationException(ApplicationError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        constraint: Optional[str] = None,
        provided_value: Any = None,
        expected_format: Optional[str] = None,
    ) -> None:
        details = ErrorDetails(
            field=field,
            constraint=constraint,
            provided_value=provided_value,
            expected_format=expected_format,
        )
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
        )


class ResourceNotFoundException(ApplicationError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: str = "resource",
        resource_id: Optional[str] = None,
    ) -> None:
        error_code = ErrorCode.NOT_FOUND
        if resource_type == "machine":
            error_code = ErrorCode.MACHINE_NOT_FOUND
        elif resource_type == "prediction":
            error_code = ErrorCode.PREDICTION_NOT_FOUND
        elif resource_type == "esg":
            error_code = ErrorCode.ESG_DATA_NOT_FOUND

        details = None
        if resource_id:
            details = ErrorDetails(field=resource_type, provided_value=resource_id)

        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            details=details,
        )


class ComputationException(ApplicationError):
    """Raised when computation/calculation fails."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.COMPUTATION_ERROR,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
        )


class DatabaseException(ApplicationError):
    """Raised when database operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
        )


class ExternalServiceException(ApplicationError):
    """Raised when external services fail."""

    def __init__(self, message: str, service_name: Optional[str] = None) -> None:
        details = None
        if service_name:
            details = ErrorDetails(field="service", provided_value=service_name)

        super().__init__(
            message=message,
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            details=details,
        )
