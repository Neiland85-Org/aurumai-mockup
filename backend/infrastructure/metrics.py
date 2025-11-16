"""
Infrastructure: Prometheus Metrics
Centralized metrics collection for observability
"""

import functools
import time
from typing import Callable, ParamSpec, TypeVar

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from infrastructure.logging import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# APPLICATION METRICS
# ============================================================================


# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "endpoint"],
)


# Database Metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

db_connections_active = Gauge(
    "db_connections_active",
    "Number of active database connections",
)


# ML Prediction Metrics
ml_predictions_total = Counter(
    "ml_predictions_total",
    "Total ML predictions",
    ["machine_type", "model_version"],
)

ml_prediction_duration_seconds = Histogram(
    "ml_prediction_duration_seconds",
    "ML prediction duration in seconds",
    ["machine_type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ml_prediction_risk_score = Histogram(
    "ml_prediction_risk_score",
    "Distribution of ML prediction risk scores",
    ["machine_type"],
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)


# Data Ingestion Metrics
data_ingestion_total = Counter(
    "data_ingestion_total",
    "Total data ingestion events",
    ["machine_id", "data_type"],
)

data_ingestion_errors_total = Counter(
    "data_ingestion_errors_total",
    "Total data ingestion errors",
    ["machine_id", "error_type"],
)

data_ingestion_duration_seconds = Histogram(
    "data_ingestion_duration_seconds",
    "Data ingestion duration in seconds",
    ["data_type"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)


# Circuit Breaker Metrics
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half_open)",
    ["name"],
)

circuit_breaker_failures_total = Counter(
    "circuit_breaker_failures_total",
    "Total circuit breaker failures",
    ["name"],
)

circuit_breaker_successes_total = Counter(
    "circuit_breaker_successes_total",
    "Total circuit breaker successes",
    ["name"],
)


# Retry Metrics
retry_attempts_total = Counter(
    "retry_attempts_total",
    "Total retry attempts",
    ["function", "attempt_number"],
)

retry_failures_total = Counter(
    "retry_failures_total",
    "Total retry failures after all attempts",
    ["function"],
)


# Error Metrics
errors_total = Counter(
    "errors_total",
    "Total errors by type",
    ["error_type", "error_code"],
)

validation_errors_total = Counter(
    "validation_errors_total",
    "Total validation errors",
    ["field", "constraint"],
)


# System Metrics
system_info = Gauge(
    "system_info",
    "System information",
    ["version", "environment"],
)


# ============================================================================
# METRIC UTILITIES
# ============================================================================


def track_request(method: str, endpoint: str, status_code: int) -> None:
    """
    Track HTTP request metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
    """
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()


def track_request_duration(method: str, endpoint: str, duration: float) -> None:
    """
    Track HTTP request duration.

    Args:
        method: HTTP method
        endpoint: API endpoint path
        duration: Duration in seconds
    """
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_db_query(operation: str, table: str, duration: float) -> None:
    """
    Track database query metrics.

    Args:
        operation: Query operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration: Duration in seconds
    """
    db_queries_total.labels(operation=operation, table=table).inc()
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)


def track_prediction(
    machine_type: str, model_version: str, duration: float, risk_score: float
) -> None:
    """
    Track ML prediction metrics.

    Args:
        machine_type: Type of machine
        model_version: ML model version
        duration: Prediction duration in seconds
        risk_score: Predicted risk score (0.0-1.0)
    """
    ml_predictions_total.labels(machine_type=machine_type, model_version=model_version).inc()
    ml_prediction_duration_seconds.labels(machine_type=machine_type).observe(duration)
    ml_prediction_risk_score.labels(machine_type=machine_type).observe(risk_score)


def track_ingestion(
    machine_id: str,
    data_type: str,
    duration: float,
    success: bool = True,
    error_type: str | None = None,
) -> None:
    """
    Track data ingestion metrics.

    Args:
        machine_id: Machine identifier
        data_type: Type of data (raw_measurement, feature_vector)
        duration: Ingestion duration in seconds
        success: Whether ingestion succeeded
        error_type: Error type if failed
    """
    data_ingestion_total.labels(machine_id=machine_id, data_type=data_type).inc()
    data_ingestion_duration_seconds.labels(data_type=data_type).observe(duration)

    if not success and error_type:
        data_ingestion_errors_total.labels(machine_id=machine_id, error_type=error_type).inc()


def track_circuit_breaker(name: str, state: str, success: bool | None = None) -> None:
    """
    Track circuit breaker metrics.

    Args:
        name: Circuit breaker name
        state: Circuit breaker state (closed/open/half_open)
        success: Whether call succeeded (if applicable)
    """
    state_map = {"closed": 0, "open": 1, "half_open": 2}
    circuit_breaker_state.labels(name=name).set(state_map.get(state, 0))

    if success is True:
        circuit_breaker_successes_total.labels(name=name).inc()
    elif success is False:
        circuit_breaker_failures_total.labels(name=name).inc()


def track_retry(function: str, attempt_number: int, final_failure: bool = False) -> None:
    """
    Track retry metrics.

    Args:
        function: Function name
        attempt_number: Retry attempt number
        final_failure: Whether all retries failed
    """
    retry_attempts_total.labels(function=function, attempt_number=str(attempt_number)).inc()

    if final_failure:
        retry_failures_total.labels(function=function).inc()


def track_error(error_type: str, error_code: str) -> None:
    """
    Track error metrics.

    Args:
        error_type: Type of error (ValidationError, DatabaseError, etc.)
        error_code: Error code
    """
    errors_total.labels(error_type=error_type, error_code=error_code).inc()


def track_validation_error(field: str, constraint: str) -> None:
    """
    Track validation error metrics.

    Args:
        field: Field that failed validation
        constraint: Constraint that was violated
    """
    validation_errors_total.labels(field=field, constraint=constraint).inc()


# ============================================================================
# DECORATORS
# ============================================================================


def track_time(
    metric: Histogram, labels: dict[str, str] | None = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to track function execution time.

    Args:
        metric: Histogram metric to update
        labels: Optional labels for the metric

    Example:
        >>> @track_time(http_request_duration_seconds,
        ...     {"method": "GET", "endpoint": "/api/machines"})
        ... def get_machines():
        ...     return {"machines": [...]}
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


# ============================================================================
# METRICS EXPORT
# ============================================================================


def get_metrics() -> bytes:
    """
    Get Prometheus metrics in text format.

    Returns:
        Metrics in Prometheus text format
    """
    return generate_latest(REGISTRY)


def reset_metrics(registry: CollectorRegistry = REGISTRY) -> None:
    """
    Reset all metrics (for testing).

    Args:
        registry: Prometheus registry to reset
    """
    collectors = list(registry._collector_to_names.keys())
    for collector in collectors:
        try:
            registry.unregister(collector)
        except Exception as e:
            logger.warning(f"Failed to unregister collector: {e}")
