"""
Infrastructure: Structured Logging with JSON Format
Centralized logging configuration with contextual fields
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, MutableMapping, Optional

from pythonjsonlogger import jsonlogger

# Context variables for request-scoped logging
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
machine_id_ctx: ContextVar[Optional[str]] = ContextVar("machine_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class ContextualJSONFormatter(jsonlogger.JsonFormatter):
    """
    JSON formatter that includes contextual fields from ContextVars.

    Fields added automatically:
    - request_id: Unique identifier for the request
    - machine_id: Machine being processed (if applicable)
    - user_id: User making the request (if applicable)
    - environment: Deployment environment (dev/staging/prod)
    """

    def __init__(self, *args: Any, environment: str = "development", **kwargs: Any) -> None:
        # Call parent init without type checking since it's untyped
        super().__init__(*args, **kwargs)  # type: ignore
        self.environment = environment

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to log records"""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Add environment
        log_record["environment"] = self.environment

        # Add contextual fields from ContextVars
        request_id = request_id_ctx.get()
        if request_id:
            log_record["request_id"] = request_id

        machine_id = machine_id_ctx.get()
        if machine_id:
            log_record["machine_id"] = machine_id

        user_id = user_id_ctx.get()
        if user_id:
            log_record["user_id"] = user_id

        # Add source location
        log_record["logger"] = record.name
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName

        # Add severity level
        log_record["severity"] = record.levelname


def setup_logging(
    level: str = "INFO",
    environment: str = "development",
    logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    Configure structured JSON logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Deployment environment (dev/staging/prod)
        logger_name: Optional logger name (defaults to root logger)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(level="DEBUG", environment="production")
        >>> logger.info("User logged in", extra={"user_id": "123"})
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = ContextualJSONFormatter(
        fmt="%(timestamp)s %(severity)s %(logger)s %(message)s",
        environment=environment,
        datefmt="%Y-%m-%dT%H:%M:%S.%fZ",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Don't propagate to root logger to avoid duplicate logs
    if logger_name:
        logger.propagate = False

    return logger


def get_logger(name: str, level: str = "INFO", environment: str = "development") -> logging.Logger:
    """
    Get or create a logger with structured JSON formatting.

    Args:
        name: Logger name (usually __name__ of the module)
        level: Logging level
        environment: Deployment environment

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing data", extra={"records": 100})
    """
    return setup_logging(level=level, environment=environment, logger_name=name)


def set_request_context(
    request_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """
    Set contextual fields for the current request.

    Args:
        request_id: Unique request identifier
        machine_id: Machine being processed
        user_id: User making the request

    Example:
        >>> set_request_context(request_id="req-123", machine_id="M001")
        >>> logger.info("Processing machine")  # Will include request_id and machine_id
    """
    if request_id is not None:
        request_id_ctx.set(request_id)
    if machine_id is not None:
        machine_id_ctx.set(machine_id)
    if user_id is not None:
        user_id_ctx.set(user_id)


def clear_request_context() -> None:
    """
    Clear all contextual fields after request processing.

    Example:
        >>> clear_request_context()
    """
    request_id_ctx.set(None)
    machine_id_ctx.set(None)
    user_id_ctx.set(None)


class LoggerAdapter(logging.LoggerAdapter):  # type: ignore[type-arg]
    """
    Logger adapter that adds extra fields to all log messages.

    Example:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {"service": "ml_engine"})
        >>> logger.info("Prediction completed")  # Will include service=ml_engine
    """

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Add extra fields to kwargs"""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
