"""
Infrastructure: Distributed Tracing with OpenTelemetry
Enables end-to-end request tracing across services
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Span, Status, StatusCode

from infrastructure.logging import get_logger


logger = get_logger(__name__)


# ============================================================================
# TRACING CONFIGURATION
# ============================================================================


def setup_tracing(
    service_name: str = "aurumai-backend",
    service_version: str = "1.0.0",
    environment: str = "development",
    otlp_endpoint: Optional[str] = None,
    console_export: bool = False,
) -> TracerProvider:
    """
    Configure OpenTelemetry tracing for the application.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        environment: Deployment environment (dev/staging/prod)
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317")
        console_export: Whether to export spans to console (for debugging)

    Returns:
        Configured TracerProvider

    Example:
        >>> provider = setup_tracing(
        ...     service_name="aurumai-backend",
        ...     environment="production",
        ...     otlp_endpoint="http://jaeger:4317"
        ... )
    """
    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment,
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint provided
    if otlp_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(
                f"OpenTelemetry OTLP exporter configured",
                extra={"endpoint": otlp_endpoint},
            )
        except Exception as e:
            logger.error(
                f"Failed to configure OTLP exporter: {e}",
                extra={"endpoint": otlp_endpoint, "error": str(e)},
            )

    # Add console exporter for debugging
    if console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("OpenTelemetry console exporter configured")

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    logger.info(
        f"OpenTelemetry tracing configured",
        extra={
            "service_name": service_name,
            "service_version": service_version,
            "environment": environment,
        },
    )

    return provider


def instrument_fastapi(app: Any) -> None:
    """
    Instrument FastAPI application with automatic tracing.

    Args:
        app: FastAPI application instance

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> instrument_fastapi(app)
    """
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


# ============================================================================
# TRACER UTILITIES
# ============================================================================


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer for a specific component.

    Args:
        name: Tracer name (usually module name)

    Returns:
        OpenTelemetry tracer instance

    Example:
        >>> tracer = get_tracer(__name__)
        >>> with tracer.start_as_current_span("process_data"):
        ...     # Your code here
        ...     pass
    """
    return trace.get_tracer(name)


def get_current_span() -> Span:
    """
    Get the current active span.

    Returns:
        Current span or a non-recording span if none active

    Example:
        >>> span = get_current_span()
        >>> span.set_attribute("user_id", "123")
    """
    return trace.get_current_span()


def set_span_attributes(attributes: dict[str, Any]) -> None:
    """
    Add attributes to the current span.

    Args:
        attributes: Dictionary of attribute key-value pairs

    Example:
        >>> set_span_attributes({
        ...     "machine_id": "M001",
        ...     "machine_type": "CNC",
        ...     "prediction_score": 0.85
        ... })
    """
    span = get_current_span()
    for key, value in attributes.items():
        span.set_attribute(key, value)


def set_span_status(success: bool, description: Optional[str] = None) -> None:
    """
    Set the status of the current span.

    Args:
        success: Whether the operation succeeded
        description: Optional status description

    Example:
        >>> try:
        ...     result = perform_operation()
        ...     set_span_status(True)
        ... except Exception as e:
        ...     set_span_status(False, str(e))
    """
    span = get_current_span()
    if success:
        span.set_status(Status(StatusCode.OK, description))
    else:
        span.set_status(Status(StatusCode.ERROR, description))


def record_exception(exception: Exception, attributes: Optional[dict[str, Any]] = None) -> None:
    """
    Record an exception in the current span.

    Args:
        exception: Exception to record
        attributes: Optional additional attributes

    Example:
        >>> try:
        ...     risky_operation()
        ... except ValueError as e:
        ...     record_exception(e, {"operation": "data_validation"})
    """
    span = get_current_span()
    span.record_exception(exception, attributes=attributes)
    span.set_status(Status(StatusCode.ERROR, str(exception)))


# ============================================================================
# CONTEXT PROPAGATION
# ============================================================================


def get_trace_context_headers() -> dict[str, str]:
    """
    Get trace context headers for propagating trace to external services.

    Returns:
        Dictionary with traceparent and tracestate headers

    Example:
        >>> headers = get_trace_context_headers()
        >>> async with httpx.AsyncClient() as client:
        ...     response = await client.get("http://api.example.com", headers=headers)
    """
    from opentelemetry.propagate import inject

    headers: dict[str, str] = {}
    inject(headers)
    return headers


def extract_trace_context(headers: dict[str, str]) -> None:
    """
    Extract trace context from incoming request headers.

    Args:
        headers: Request headers

    Example:
        >>> # In FastAPI endpoint
        >>> @app.get("/endpoint")
        >>> async def endpoint(request: Request):
        ...     extract_trace_context(dict(request.headers))
        ...     # Processing continues with trace context
    """
    from opentelemetry.propagate import extract

    extract(headers)


# ============================================================================
# CUSTOM SPANS
# ============================================================================


class traced_operation:
    """
    Context manager for creating custom spans.

    Example:
        >>> with traced_operation("fetch_machine_data", {"machine_id": "M001"}):
        ...     data = fetch_data()
    """

    def __init__(
        self,
        operation_name: str,
        attributes: Optional[dict[str, Any]] = None,
        tracer_name: Optional[str] = None,
    ) -> None:
        """
        Initialize traced operation.

        Args:
            operation_name: Name of the operation
            attributes: Optional attributes to add to the span
            tracer_name: Optional tracer name (defaults to module name)
        """
        self.operation_name = operation_name
        self.attributes = attributes or {}
        self.tracer = get_tracer(tracer_name or __name__)
        self.span: Optional[Span] = None

    def __enter__(self) -> Span:
        """Start the span"""
        self.span = self.tracer.start_span(self.operation_name)
        assert self.span is not None
        self.span.__enter__()

        # Add attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)

        return self.span

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End the span and record any exception"""
        if self.span:
            if exc_val:
                self.span.record_exception(exc_val)
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            else:
                self.span.set_status(Status(StatusCode.OK))

            self.span.__exit__(exc_type, exc_val, exc_tb)


async def traced_async_operation(
    operation_name: str,
    attributes: Optional[dict[str, Any]] = None,
):
    """
    Async context manager for creating custom spans.

    Example:
        >>> async with traced_async_operation("fetch_predictions", {"limit": 50}):
        ...     predictions = await fetch_predictions()
    """
    tracer = get_tracer(__name__)
    span = tracer.start_span(operation_name)

    # Add attributes
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    try:
        yield span
        span.set_status(Status(StatusCode.OK))
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise
    finally:
        span.end()


# ============================================================================
# DEBUGGING
# ============================================================================


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID as a hex string.

    Returns:
        Trace ID or None if no active span

    Example:
        >>> trace_id = get_trace_id()
        >>> logger.info(f"Processing request", extra={"trace_id": trace_id})
    """
    span = get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")
    return None


def get_span_id() -> Optional[str]:
    """
    Get the current span ID as a hex string.

    Returns:
        Span ID or None if no active span

    Example:
        >>> span_id = get_span_id()
        >>> logger.debug(f"Operation started", extra={"span_id": span_id})
    """
    span = get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, "016x")
    return None


def is_tracing_enabled() -> bool:
    """
    Check if tracing is enabled and active.

    Returns:
        True if tracing is enabled

    Example:
        >>> if is_tracing_enabled():
        ...     set_span_attributes({"detailed_info": complex_data})
    """
    span = get_current_span()
    return span.get_span_context().is_valid if span else False
