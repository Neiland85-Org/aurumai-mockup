"""
Infrastructure: Resilience Patterns (Retry, Circuit Breaker, Timeout)
Implements reliability patterns for external service calls
"""

import asyncio
import functools
from typing import Any, Callable, ParamSpec, TypeVar

import httpx
from pybreaker import CircuitBreaker, CircuitBreakerError
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from infrastructure.logging import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


# ============================================================================
# RETRY POLICIES
# ============================================================================


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.

    Example:
        >>> policy = RetryPolicy(max_attempts=3, base_delay=1.0, max_delay=10.0)
        >>> result = await policy.execute_async(fetch_data, url="http://api.example.com")
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        multiplier: float = 2.0,
        retryable_exceptions: tuple[type[Exception], ...] = (
            httpx.RequestError,
            httpx.TimeoutException,
            ConnectionError,
        ),
    ) -> None:
        """
        Initialize retry policy.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            multiplier: Exponential backoff multiplier
            retryable_exceptions: Tuple of exception types to retry
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.retryable_exceptions = retryable_exceptions

    def execute(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute function with retry policy (synchronous).

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            RetryError: If all retry attempts fail
        """
        retryer = Retrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.base_delay,
                max=self.max_delay,
            ),
            retry=retry_if_exception_type(self.retryable_exceptions),
            reraise=True,
        )

        try:
            for attempt in retryer:
                with attempt:
                    logger.debug(
                        f"Executing {func.__name__} "
                        f"(attempt {attempt.retry_state.attempt_number}/{self.max_attempts})",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt.retry_state.attempt_number,
                            "max_attempts": self.max_attempts,
                        },
                    )
                    return func(*args, **kwargs)
        except RetryError as e:
            logger.error(
                f"All retry attempts failed for {func.__name__}",
                extra={
                    "function": func.__name__,
                    "attempts": self.max_attempts,
                    "error": str(e.last_attempt.exception()),
                },
            )
            raise

        # This should never be reached, but keeps type checker happy
        raise RuntimeError("Retry logic failed unexpectedly")

    async def execute_async(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute async function with retry policy.

        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            RetryError: If all retry attempts fail
        """
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.base_delay,
                max=self.max_delay,
            ),
            retry=retry_if_exception_type(self.retryable_exceptions),
            reraise=True,
        )

        try:
            async for attempt in retryer:
                with attempt:
                    logger.debug(
                        f"Executing {func.__name__} "
                        f"(attempt {attempt.retry_state.attempt_number}/{self.max_attempts})",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt.retry_state.attempt_number,
                            "max_attempts": self.max_attempts,
                        },
                    )
                    return await func(*args, **kwargs)
        except RetryError as e:
            logger.error(
                f"All retry attempts failed for {func.__name__}",
                extra={
                    "function": func.__name__,
                    "attempts": self.max_attempts,
                    "error": str(e.last_attempt.exception()),
                },
            )
            raise

        # This should never be reached, but keeps type checker happy
        raise RuntimeError("Retry logic failed unexpectedly")


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to add retry logic to a function.

    Example:
        >>> @with_retry(max_attempts=3, base_delay=1.0)
        ... def fetch_data(url: str) -> dict:
        ...     response = httpx.get(url)
        ...     return response.json()
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        policy = RetryPolicy(max_attempts=max_attempts, base_delay=base_delay, max_delay=max_delay)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return policy.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def with_async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to add retry logic to an async function.

    Example:
        >>> @with_async_retry(max_attempts=3, base_delay=1.0)
        ... async def fetch_data(url: str) -> dict:
        ...     async with httpx.AsyncClient() as client:
        ...         response = await client.get(url)
        ...         return response.json()
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        policy = RetryPolicy(max_attempts=max_attempts, base_delay=base_delay, max_delay=max_delay)

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await policy.execute_async(func, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# CIRCUIT BREAKERS
# ============================================================================


class ResilientCircuitBreaker(CircuitBreaker):
    """
    Circuit breaker with logging and metrics integration.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failures exceeded threshold, requests fail immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed

    Example:
        >>> breaker = ResilientCircuitBreaker(
        ...     name="backend_api",
        ...     fail_max=5,
        ...     timeout_duration=60
        ... )
        >>> result = breaker.call(send_request, url="http://api.example.com")
    """

    def __init__(
        self,
        name: str,
        fail_max: int = 5,
        timeout_duration: float = 60.0,
        expected_exception: type[Exception] = Exception,
        **kwargs: Any,
    ) -> None:
        """
        Initialize circuit breaker.

        Args:
            name: Unique name for this circuit breaker
            fail_max: Number of failures before opening circuit
            timeout_duration: Seconds to wait before attempting recovery
            expected_exception: Exception type that triggers circuit opening
            **kwargs: Additional arguments for CircuitBreaker
        """
        super().__init__(
            fail_max=fail_max,
            timeout_duration=timeout_duration,
            expected_exception=expected_exception,
            name=name,
            **kwargs,
        )

        # Add listeners for state changes
        self.add_listener(self._on_state_change)

    def _on_state_change(self, breaker: CircuitBreaker, old_state: str, new_state: str) -> None:
        """Log circuit breaker state changes"""
        logger.warning(
            f"Circuit breaker '{breaker.name}' state changed: {old_state} -> {new_state}",
            extra={
                "circuit_breaker": breaker.name,
                "old_state": old_state,
                "new_state": new_state,
                "fail_count": breaker.fail_counter,
                "fail_max": breaker.fail_max,
            },
        )

    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute function through circuit breaker (synchronous).

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the function

        Raises:
            CircuitBreakerError: If circuit is open
        """
        try:
            result = super().call(func, *args, **kwargs)
            logger.debug(
                f"Circuit breaker '{self.name}' call succeeded",
                extra={"circuit_breaker": self.name, "state": self.current_state},
            )
        except CircuitBreakerError:
            logger.error(
                f"Circuit breaker '{self.name}' is OPEN, rejecting call",
                extra={
                    "circuit_breaker": self.name,
                    "state": self.current_state,
                    "fail_count": self.fail_counter,
                },
            )
            raise
        else:
            return result

    async def call_async(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute async function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the function

        Raises:
            CircuitBreakerError: If circuit is open
        """
        try:
            result = await super().call_async(func, *args, **kwargs)
            logger.debug(
                f"Circuit breaker '{self.name}' async call succeeded",
                extra={"circuit_breaker": self.name, "state": self.current_state},
            )
        except CircuitBreakerError:
            logger.error(
                f"Circuit breaker '{self.name}' is OPEN, rejecting async call",
                extra={
                    "circuit_breaker": self.name,
                    "state": self.current_state,
                    "fail_count": self.fail_counter,
                },
            )
            raise
        else:
            return result


# ============================================================================
# TIMEOUT UTILITIES
# ============================================================================


class TimeoutConfig:
    """
    Centralized timeout configuration for HTTP clients and database operations.

    Example:
        >>> config = TimeoutConfig(connect=5.0, read=30.0)
        >>> timeout = config.as_httpx_timeout()
    """

    def __init__(
        self,
        connect: float = 5.0,
        read: float = 30.0,
        write: float = 30.0,
        pool: float = 5.0,
    ) -> None:
        """
        Initialize timeout configuration.

        Args:
            connect: Connection timeout in seconds
            read: Read timeout in seconds
            write: Write timeout in seconds
            pool: Pool timeout in seconds (time to acquire connection)
        """
        self.connect = connect
        self.read = read
        self.write = write
        self.pool = pool

    def as_httpx_timeout(self) -> httpx.Timeout:
        """
        Convert to httpx.Timeout object.

        Returns:
            httpx.Timeout configuration
        """
        return httpx.Timeout(
            connect=self.connect,
            read=self.read,
            write=self.write,
            pool=self.pool,
        )

    def as_dict(self) -> dict[str, float]:
        """
        Convert to dictionary.

        Returns:
            Dictionary with timeout values
        """
        return {
            "connect": self.connect,
            "read": self.read,
            "write": self.write,
            "pool": self.pool,
        }


async def with_timeout(coro: Any, timeout: float) -> Any:
    """
    Execute coroutine with timeout.

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds

    Returns:
        Result of the coroutine

    Raises:
        asyncio.TimeoutError: If timeout is exceeded

    Example:
        >>> result = await with_timeout(fetch_data(), timeout=10.0)
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(
            f"Operation timed out after {timeout}s",
            extra={"timeout": timeout},
        )
        raise
