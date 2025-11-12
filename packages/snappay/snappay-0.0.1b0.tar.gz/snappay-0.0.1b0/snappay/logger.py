"""Logging configuration for SnapPay SDK.

This module provides centralized logging configuration with features like:
- Structured logging
- Request/response logging
- Sensitive data redaction
- Performance tracking
"""

import logging
import sys
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

from .utils import sanitize_log_data


class SnapPayLogger:
    """Custom logger for SnapPay SDK with enhanced features."""

    def __init__(
        self,
        name: str = "snappay",
        level: str = "INFO",
        log_requests: bool = False,
        log_responses: bool = False,
        redact_sensitive: bool = True,
    ):
        """Initialize SnapPay logger.

        Args:
            name: Logger name
            level: Logging level
            log_requests: Whether to log HTTP requests
            log_responses: Whether to log HTTP responses
            redact_sensitive: Whether to redact sensitive data
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.redact_sensitive = redact_sensitive

        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(getattr(logging, level.upper()))

            # Use structured format
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional context."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional context."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional context."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with optional context."""
        self._log(logging.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method with data sanitization.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context to log
        """
        extra = {}
        if kwargs:
            # Sanitize sensitive data if enabled
            if self.redact_sensitive:
                extra = sanitize_log_data(kwargs)
            else:
                extra = kwargs

        # Format extra data
        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            message = f"{message} | {extra_str}"

        self.logger.log(level, message)

    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> None:
        """Log HTTP request details.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request body data
            params: Query parameters
        """
        if not self.log_requests:
            return

        log_data = {
            "method": method,
            "url": url,
        }

        if headers:
            log_data["headers"] = (
                headers if not self.redact_sensitive else sanitize_log_data(headers)  # type: ignore[assignment]
            )

        if data:
            log_data["body"] = (
                data if not self.redact_sensitive else sanitize_log_data(data)
            )

        if params:
            log_data["params"] = params  # type: ignore[assignment]

        self.debug(f"API Request: {method} {url}", **log_data)

    def log_response(
        self,
        status: int,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log HTTP response details.

        Args:
            status: Response status code
            url: Request URL
            headers: Response headers
            data: Response body data
            duration: Request duration in seconds
        """
        if not self.log_responses:
            return

        log_data = {
            "status": status,
            "url": url,
        }

        if headers:
            log_data["headers"] = (
                headers if not self.redact_sensitive else sanitize_log_data(headers)
            )

        if data:
            log_data["body"] = (
                data if not self.redact_sensitive else sanitize_log_data(data)
            )

        if duration is not None:
            log_data["duration_ms"] = f"{duration * 1000:.2f}"

        level = logging.DEBUG if 200 <= status < 400 else logging.WARNING
        self.logger.log(level, f"API Response: {status} from {url}", extra=log_data)

    @contextmanager
    def timer(self, operation: str):
        """Context manager to time operations.

        Args:
            operation: Name of the operation being timed

        Example:
            >>> with logger.timer("api_call"):
            >>>     result = await make_api_call()
        """
        start_time = time.time()
        self.debug(f"Starting: {operation}")

        try:
            yield
        finally:
            duration = time.time() - start_time
            self.debug(
                f"Completed: {operation}",
                duration_ms=f"{duration * 1000:.2f}",
            )

    def log_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log exception with context.

        Args:
            error: Exception to log
            context: Additional context about the error
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        if context:
            error_data.update(context)

        # Add specific error attributes if available
        if hasattr(error, "status_code"):
            error_data["status_code"] = error.status_code
        if hasattr(error, "error_code"):
            error_data["error_code"] = error.error_code
        if hasattr(error, "request_id"):
            error_data["request_id"] = error.request_id

        self.error(f"Exception occurred: {type(error).__name__}", **error_data)


def get_logger(
    name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> SnapPayLogger:
    """Get or create a SnapPay logger instance.

    Args:
        name: Logger name (defaults to "snappay")
        config: Logger configuration

    Returns:
        SnapPayLogger instance
    """
    if name is None:
        name = "snappay"

    if config is None:
        config = {}

    return SnapPayLogger(
        name=name,
        level=config.get("level", "INFO"),
        log_requests=config.get("log_requests", False),
        log_responses=config.get("log_responses", False),
        redact_sensitive=config.get("redact_sensitive", True),
    )


def log_method_call(func: Callable) -> Callable:
    """Decorator to log method calls with arguments.

    Args:
        func: Function to decorate

    Returns:
        Decorated function

    Example:
        >>> @log_method_call
        >>> async def api_method(self, arg1, arg2):
        >>>     return await self._make_request()
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger()

        # Get method name and class if available
        method_name = func.__name__
        class_name = (
            args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else ""
        )
        full_name = f"{class_name}.{method_name}" if class_name else method_name

        # Log method entry
        logger.debug(
            f"Calling: {full_name}",
            args=str(args[1:])[:100] if len(args) > 1 else None,
            kwargs=str(kwargs)[:100] if kwargs else None,
        )

        try:
            # Execute method
            result = await func(*args, **kwargs)
            logger.debug(f"Success: {full_name}")
            return result

        except Exception as e:
            logger.error(
                f"Failed: {full_name}",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    return wrapper


class RequestLogger:
    """Context manager for logging API requests with timing."""

    def __init__(self, logger: SnapPayLogger, operation: str):
        """Initialize request logger.

        Args:
            logger: SnapPayLogger instance
            operation: Name of the operation
        """
        self.logger = logger
        self.operation = operation
        self.start_time: Optional[float] = None

    def __enter__(self):
        """Start timing the request."""
        self.start_time = time.time()
        self.logger.debug(f"Starting API operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log request completion with timing."""
        duration = time.time() - (self.start_time or 0.0)

        if exc_type is None:
            self.logger.debug(
                f"Completed API operation: {self.operation}",
                duration_ms=f"{duration * 1000:.2f}",
            )
        else:
            self.logger.error(
                f"Failed API operation: {self.operation}",
                duration_ms=f"{duration * 1000:.2f}",
                error_type=exc_type.__name__,
                error=str(exc_val),
            )


# Default logger instance
default_logger = get_logger()
