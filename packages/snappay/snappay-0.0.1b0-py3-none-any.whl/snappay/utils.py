"""Utility functions for SnapPay SDK.

This module provides common utility functions including retry logic,
validation helpers, and data transformation utilities.
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import aiohttp

from .constants import RETRYABLE_STATUS_CODES
from .types import RateLimitError, SnapPayError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryHandler:
    """Handles retry logic with exponential backoff and jitter.

    This class implements a sophisticated retry mechanism with:
    - Exponential backoff
    - Jitter to prevent thundering herd
    - Respect for rate limit headers
    - Configurable retry conditions

    Example:
        >>> retry_handler = RetryHandler(max_retries=3, base_delay=1.0)
        >>> result = await retry_handler.execute(async_function, arg1, arg2)
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.base_delay * (self.exponential_base**attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter
        if self.jitter:
            delay *= 0.5 + random.random()

        return delay

    def should_retry(self, error: Exception) -> bool:
        """Determine if an error is retryable.

        Args:
            error: The exception that occurred

        Returns:
            True if the error is retryable
        """
        # Check for network errors
        if isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError)):
            return True

        # Check for retryable HTTP status codes
        if isinstance(error, SnapPayError) and error.status_code:
            return error.status_code in RETRYABLE_STATUS_CODES

        return False

    def extract_retry_after(self, error: Exception) -> Optional[float]:
        """Extract retry-after delay from error if available.

        Args:
            error: The exception that occurred

        Returns:
            Retry-after delay in seconds, or None
        """
        if isinstance(error, RateLimitError):
            # Check for retry_after attribute
            if hasattr(error, "retry_after"):
                return error.retry_after

        return None

    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """Execute a function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function execution

        Raises:
            The last exception if all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)  # type: ignore[no-any-return,misc]

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if attempt >= self.max_retries or not self.should_retry(e):
                    raise

                # Calculate delay
                retry_after = self.extract_retry_after(e)
                if retry_after:
                    delay = retry_after
                else:
                    delay = self.calculate_delay(attempt)

                logger.warning(
                    f"Retry attempt {attempt + 1}/{self.max_retries} "
                    f"after {delay:.2f}s delay. Error: {e}"
                )

                await asyncio.sleep(delay)

        # This should never be reached, but for type safety
        raise last_exception or Exception("Retry failed")


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> Callable:
    """Decorator to add retry logic to async functions.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry_on_failure(max_retries=3)
        >>> async def api_call():
        >>>     return await make_request()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            handler = RetryHandler(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
            )
            return await handler.execute(func, *args, **kwargs)

        return wrapper

    return decorator


class Validator:
    """Validation utilities for API parameters."""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    URL_REGEX = re.compile(r"^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:/.*)?$")

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid email format
        """
        if not email or not isinstance(email, str):
            return False
        return bool(cls.EMAIL_REGEX.match(email.strip()))

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL format.

        Args:
            url: URL to validate

        Returns:
            True if valid URL format
        """
        if not url or not isinstance(url, str):
            return False
        return bool(cls.URL_REGEX.match(url.strip()))

    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """Validate API key format.

        Args:
            api_key: API key to validate

        Returns:
            True if valid API key format
        """
        if not api_key or not isinstance(api_key, str):
            return False

        api_key = api_key.strip()
        valid_prefixes = ("pk_test_", "pk_live_")
        return any(api_key.startswith(prefix) for prefix in valid_prefixes)

    @classmethod
    def validate_customer_id(cls, customer_id: str) -> bool:
        """Validate customer ID format.

        Args:
            customer_id: Customer ID to validate

        Returns:
            True if valid customer ID
        """
        if not customer_id or not isinstance(customer_id, str):
            return False

        customer_id = customer_id.strip()
        return 1 <= len(customer_id) <= 255

    @classmethod
    def validate_amount(cls, amount: Union[int, float]) -> bool:
        """Validate monetary amount.

        Args:
            amount: Amount to validate

        Returns:
            True if valid amount
        """
        if not isinstance(amount, (int, float)):
            return False
        return amount >= 0

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> bool:
        """Validate metadata dictionary.

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            True if valid metadata
        """
        if not isinstance(metadata, dict):
            return False

        # Check size limit (16KB)
        try:
            json_str = json.dumps(metadata)
            if len(json_str.encode("utf-8")) > 16384:
                return False
        except (TypeError, ValueError):
            return False

        return True


class DataTransformer:
    """Utilities for data transformation and formatting."""

    @staticmethod
    def to_cents(amount: Union[int, float]) -> int:
        """Convert amount to cents (integer).

        Args:
            amount: Amount in dollars

        Returns:
            Amount in cents
        """
        return int(round(amount * 100))

    @staticmethod
    def from_cents(cents: int) -> float:
        """Convert cents to dollars (float).

        Args:
            cents: Amount in cents

        Returns:
            Amount in dollars
        """
        return cents / 100.0

    @staticmethod
    def to_iso8601(dt: datetime) -> str:
        """Convert datetime to ISO 8601 string.

        Args:
            dt: Datetime object

        Returns:
            ISO 8601 formatted string
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    @staticmethod
    def from_iso8601(date_string: str) -> datetime:
        """Parse ISO 8601 string to datetime.

        Args:
            date_string: ISO 8601 formatted string

        Returns:
            Datetime object
        """
        # Handle various ISO 8601 formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_string, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

        # Try with fromisoformat as fallback
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 date string: {date_string}")

    @staticmethod
    def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata for API submission.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Sanitized metadata dictionary
        """
        if not metadata:
            return {}

        sanitized = {}
        for key, value in metadata.items():
            # Convert key to string
            key = str(key)[:100]  # Limit key length

            # Convert value to JSON-serializable format
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                try:
                    # Ensure it's JSON serializable
                    json.dumps(value)
                    sanitized[key] = value  # type: ignore[assignment]
                except (TypeError, ValueError):
                    sanitized[key] = str(value)
            else:
                sanitized[key] = str(value)

        return sanitized


class IdempotencyKeyGenerator:
    """Generate and manage idempotency keys for API requests."""

    @staticmethod
    def generate() -> str:
        """Generate a unique idempotency key.

        Returns:
            UUID-based idempotency key
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_from_data(data: Dict[str, Any]) -> str:
        """Generate deterministic idempotency key from data.

        Args:
            data: Data to generate key from

        Returns:
            Hash-based idempotency key
        """
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(sorted_data.encode("utf-8"))
        return hash_obj.hexdigest()

    @staticmethod
    def is_valid(key: str) -> bool:
        """Check if idempotency key is valid.

        Args:
            key: Idempotency key to validate

        Returns:
            True if valid
        """
        if not key or not isinstance(key, str):
            return False
        return 1 <= len(key) <= 255


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []

    def is_allowed(self) -> bool:
        """Check if a request is allowed.

        Returns:
            True if request is allowed
        """
        now = time.time()
        # Remove old requests outside window
        self.requests = [t for t in self.requests if t > now - self.window_seconds]

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False

    def reset(self) -> None:
        """Reset the rate limiter."""
        self.requests.clear()


def sanitize_log_data(data: Any, redact_keys: Optional[List[str]] = None) -> Any:
    """Sanitize sensitive data for logging.

    Args:
        data: Data to sanitize
        redact_keys: List of keys to redact

    Returns:
        Sanitized data safe for logging
    """
    if redact_keys is None:
        redact_keys = [
            "api_key",
            "password",
            "secret",
            "token",
            "authorization",
            "x-api-key",
        ]

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(redact_key in key.lower() for redact_key in redact_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_log_data(value, redact_keys)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item, redact_keys) for item in data]
    elif isinstance(data, str):
        # Check if it looks like an API key
        if data.startswith(("pk_test_", "pk_live_", "sk_test_", "sk_live_")):
            return f"{data[:10]}...***REDACTED***"
        return data
    else:
        return data


def chunked_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Example:
        >>> chunked_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
