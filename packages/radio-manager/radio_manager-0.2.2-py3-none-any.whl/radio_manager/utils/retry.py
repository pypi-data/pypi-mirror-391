"""
Retry utilities for handling transient failures in radio communication.

Provides retry logic with exponential backoff for operations that may
experience temporary timeouts or connection issues.
"""

import time
import logging
from typing import Callable, TypeVar, Optional, Tuple, Type
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_timeout(
    max_retries: int = 5,
    backoff_base: float = 2.0,
    quiet_threshold: int = 1,
    timeout_exceptions: Tuple[Type[Exception], ...] = (TimeoutError,)
):
    """
    Decorator that retries a function on timeout with exponential backoff.

    Args:
        max_retries: Maximum number of consecutive timeouts before giving up
        backoff_base: Base for exponential backoff calculation (2^n seconds)
        quiet_threshold: Only log warnings after this many consecutive failures
        timeout_exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function that will retry on timeout

    Raises:
        MaxRetriesExceeded: When max_retries consecutive timeouts occur

    Example:
        @retry_on_timeout(max_retries=5, quiet_threshold=1)
        def get_radio_info(radio):
            return radio.get_reception_info()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            timeout_count = 0

            while True:
                try:
                    result = func(*args, **kwargs)

                    # If successful after previous timeouts, log recovery
                    if timeout_count > quiet_threshold:
                        logger.info(
                            f"{func.__name__}: Timeout resolved after "
                            f"{timeout_count} failures"
                        )

                    return result

                except timeout_exceptions as e:
                    timeout_count += 1
                    backoff_time = backoff_base ** (timeout_count - 1)

                    # Check if we've hit the limit
                    if timeout_count >= max_retries:
                        logger.error(
                            f"{func.__name__}: Maximum consecutive timeouts "
                            f"({max_retries}) reached"
                        )
                        raise MaxRetriesExceeded(
                            f"Maximum consecutive timeouts ({max_retries}) "
                            f"reached for {func.__name__}"
                        ) from e

                    # Only warn for excessive failures
                    if timeout_count > quiet_threshold:
                        logger.warning(
                            f"{func.__name__}: Timeout "
                            f"({timeout_count}/{max_retries}). "
                            f"Retrying in {backoff_time} seconds..."
                        )

                    # Wait before retry
                    time.sleep(backoff_time)

        return wrapper
    return decorator


def with_retry(
    func: Callable[..., T],
    max_retries: int = 5,
    backoff_base: float = 2.0,
    quiet_threshold: int = 1,
    timeout_exceptions: Tuple[Type[Exception], ...] = (TimeoutError,),
    context_name: Optional[str] = None
) -> T:
    """
    Execute a function with retry logic (functional approach).

    This is an alternative to the decorator when you want to apply retry
    logic inline without decorating the function.

    Args:
        func: Function to execute with retry logic
        max_retries: Maximum number of consecutive timeouts before giving up
        backoff_base: Base for exponential backoff calculation (2^n seconds)
        quiet_threshold: Only log warnings after this many consecutive failures
        timeout_exceptions: Tuple of exception types to catch and retry
        context_name: Optional name for logging (defaults to func.__name__)

    Returns:
        Result of successful function execution

    Raises:
        MaxRetriesExceeded: When max_retries consecutive timeouts occur

    Example:
        info = with_retry(
            lambda: radio.get_reception_info(),
            max_retries=5,
            context_name="radio.get_reception_info"
        )
    """
    timeout_count = 0
    name = context_name or getattr(func, '__name__', 'function')

    while True:
        try:
            result = func()

            # If successful after previous timeouts, log recovery
            if timeout_count > quiet_threshold:
                logger.info(
                    f"{name}: Timeout resolved after "
                    f"{timeout_count} failures"
                )

            return result

        except timeout_exceptions as e:
            timeout_count += 1
            backoff_time = backoff_base ** (timeout_count - 1)

            # Check if we've hit the limit
            if timeout_count >= max_retries:
                logger.error(
                    f"{name}: Maximum consecutive timeouts "
                    f"({max_retries}) reached"
                )
                raise MaxRetriesExceeded(
                    f"Maximum consecutive timeouts ({max_retries}) "
                    f"reached for {name}"
                ) from e

            # Only warn for excessive failures
            if timeout_count > quiet_threshold:
                logger.warning(
                    f"{name}: Timeout "
                    f"({timeout_count}/{max_retries}). "
                    f"Retrying in {backoff_time} seconds..."
                )

            # Wait before retry
            time.sleep(backoff_time)


class MaxRetriesExceeded(Exception):
    """Raised when maximum number of retries is exceeded."""
    pass
