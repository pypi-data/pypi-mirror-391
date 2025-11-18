"""Retry logic for network operations.

DEPRECATED: This module is no longer used by collectors.
Collectors now use Crawl4AI which has built-in retry logic.

Kept for backward compatibility with other parts of the codebase that may still use it.
"""

import time
from typing import Callable, TypeVar, Any

import requests

T = TypeVar("T")


def fetch_with_retry(
    url: str,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    **kwargs: Any,
) -> requests.Response:
    """Fetch URL with automatic retry and exponential backoff.

    Args:
        url: URL to fetch
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        **kwargs: Additional arguments to pass to requests.get

    Returns:
        Response object

    Raises:
        requests.RequestException: If all retry attempts fail
    """
    delay = initial_delay
    last_exception: Exception | None = None

    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except (requests.RequestException, ConnectionError) as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay)
                delay = min(delay * exponential_base, max_delay)

    if last_exception:
        raise last_exception
    raise requests.RequestException(f"Failed to fetch {url} after {max_attempts} attempts")


def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (
        requests.RequestException,
        ConnectionError,
    ),
) -> Callable[..., T]:
    """Decorator for retrying functions with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retryable_exceptions: Tuple of exception types to retry on

    Returns:
        Wrapped function with retry logic
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        delay = initial_delay
        last_exception: Exception | None = None

        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except retryable_exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

        if last_exception:
            raise last_exception
        raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts")

    return wrapper

