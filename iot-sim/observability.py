"""
Observability Infrastructure for IoT Simulator

Simplified version adapted from backend infrastructure:
- JSON structured logging
- Retry policies with exponential backoff
- Circuit breaker for backend connection
- Configurable timeouts
"""

import logging
import sys
from typing import Optional, Callable, TypeVar, Any
from contextvars import ContextVar
from datetime import datetime

from pythonjsonlogger import jsonlogger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from pybreaker import CircuitBreaker, CircuitBreakerError
import httpx


# ============================================================================
# STRUCTURED JSON LOGGING
# ============================================================================

# Context variables for request tracking
machine_id_ctx: ContextVar[Optional[str]] = ContextVar("machine_id", default=None)
sample_number_ctx: ContextVar[Optional[int]] = ContextVar("sample_number", default=None)


class IoTJSONFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with IoT-specific fields
    
    Adds:
    - timestamp (ISO 8601)
    - machine_id (from context)
    - sample_number (from context)
    - environment
    """
    
    def __init__(self, environment: str = "development", *args: Any, **kwargs: Any):
        self.environment = environment
        super().__init__(*args, **kwargs)
    
    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add severity level
        log_record["severity"] = record.levelname
        
        # Add logger name
        log_record["logger"] = record.name
        
        # Add environment
        log_record["environment"] = self.environment
        
        # Add contextual data from ContextVars
        machine_id = machine_id_ctx.get()
        if machine_id:
            log_record["machine_id"] = machine_id
        
        sample_number = sample_number_ctx.get()
        if sample_number is not None:
            log_record["sample_number"] = sample_number
        
        # Add source location
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName


def setup_logging(
    level: str = "INFO",
    environment: str = "development",
    component: str = "iot-simulator"
) -> logging.Logger:
    """
    Configure JSON structured logging for IoT simulator
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment name (development, staging, production)
        component: Component name for identification
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(component)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = IoTJSONFormatter(
        environment=environment,
        format="%(timestamp)s %(severity)s %(logger)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(
        "Logging initialized",
        extra={
            "component": component,
            "environment": environment,
            "log_level": level
        }
    )
    
    return logger


def set_sample_context(machine_id: str, sample_number: int) -> None:
    """Set context for current sample (thread-safe via ContextVars)"""
    machine_id_ctx.set(machine_id)
    sample_number_ctx.set(sample_number)


def clear_sample_context() -> None:
    """Clear sample context"""
    machine_id_ctx.set(None)
    sample_number_ctx.set(None)


# ============================================================================
# RESILIENCE - RETRY POLICIES
# ============================================================================

T = TypeVar("T")


def create_retry_decorator(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    multiplier: float = 2.0,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        multiplier: Backoff multiplier (delay *= multiplier)
        logger: Logger instance for logging retry attempts
    
    Returns:
        Decorator function
    
    Example:
        @create_retry_decorator(max_attempts=3, base_delay=1.0)
        def publish_data(data):
            return requests.post(url, json=data)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=multiplier,
            min=base_delay,
            max=max_delay
        ),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


# ============================================================================
# RESILIENCE - CIRCUIT BREAKER
# ============================================================================

class IoTCircuitBreaker(CircuitBreaker):
    """
    Circuit Breaker for IoT simulator backend connection
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked immediately
    - HALF_OPEN: Testing recovery, limited requests allowed
    
    Transitions:
    - CLOSED → OPEN: After fail_max consecutive failures
    - OPEN → HALF_OPEN: After timeout_duration seconds
    - HALF_OPEN → CLOSED: After successful request
    - HALF_OPEN → OPEN: After any failure
    """
    
    def __init__(
        self,
        name: str = "iot-backend-connection",
        fail_max: int = 5,
        timeout_duration: float = 60.0,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            fail_max=fail_max,
            timeout_duration=timeout_duration,
            name=name
        )
        self.logger = logger or logging.getLogger(__name__)
        
        # Register state change listeners
        self.add_listener(self._on_state_change)
    
    def _on_state_change(
        self,
        cb: CircuitBreaker,
        old_state: str,
        new_state: str
    ) -> None:
        """Log circuit breaker state changes"""
        self.logger.warning(
            "Circuit breaker state changed",
            extra={
                "circuit_breaker": self.name,
                "old_state": old_state,
                "new_state": new_state,
                "fail_counter": self.fail_counter
            }
        )


def create_circuit_breaker(
    name: str = "iot-backend",
    fail_max: int = 5,
    timeout_duration: float = 60.0,
    logger: Optional[logging.Logger] = None
) -> IoTCircuitBreaker:
    """
    Create a circuit breaker for backend connection
    
    Args:
        name: Circuit breaker identifier
        fail_max: Max consecutive failures before opening
        timeout_duration: Seconds before attempting recovery
        logger: Logger instance
    
    Returns:
        Circuit breaker instance
    """
    return IoTCircuitBreaker(
        name=name,
        fail_max=fail_max,
        timeout_duration=timeout_duration,
        logger=logger
    )


# ============================================================================
# TIMEOUTS
# ============================================================================

def create_timeout_config(
    connect: float = 5.0,
    read: float = 30.0,
    write: float = 30.0,
    pool: float = 5.0
) -> httpx.Timeout:
    """
    Create httpx timeout configuration
    
    Args:
        connect: Timeout for establishing connection (seconds)
        read: Timeout for reading response (seconds)
        write: Timeout for sending request (seconds)
        pool: Timeout for acquiring connection from pool (seconds)
    
    Returns:
        httpx.Timeout instance
    """
    return httpx.Timeout(
        connect=connect,
        read=read,
        write=write,
        pool=pool
    )


# ============================================================================
# DEFAULT CONFIGURATION
# ============================================================================

# Default timeout for IoT simulator
DEFAULT_TIMEOUT = create_timeout_config(
    connect=5.0,
    read=30.0,
    write=30.0,
    pool=5.0
)

# Default retry configuration
DEFAULT_RETRY_CONFIG = {
    "max_attempts": 3,
    "base_delay": 1.0,
    "max_delay": 30.0,
    "multiplier": 2.0
}

# Default circuit breaker configuration
DEFAULT_CIRCUIT_BREAKER_CONFIG = {
    "name": "iot-backend-connection",
    "fail_max": 5,
    "timeout_duration": 60.0
}


__all__ = [
    # Logging
    "setup_logging",
    "set_sample_context",
    "clear_sample_context",
    "IoTJSONFormatter",
    
    # Retry
    "create_retry_decorator",
    "DEFAULT_RETRY_CONFIG",
    
    # Circuit Breaker
    "create_circuit_breaker",
    "IoTCircuitBreaker",
    "CircuitBreakerError",
    "DEFAULT_CIRCUIT_BREAKER_CONFIG",
    
    # Timeouts
    "create_timeout_config",
    "DEFAULT_TIMEOUT",
]
