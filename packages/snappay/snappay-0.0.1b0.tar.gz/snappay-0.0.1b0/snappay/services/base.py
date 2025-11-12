"""Base service module for SnapPay SDK.

Provides BaseService class with shared HTTP client functionality including:
- Automatic retry with exponential backoff
- Request/response logging
- Error handling and mapping
- Rate limit handling
- Pagination support
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union

import aiohttp

from ..constants import RETRYABLE_STATUS_CODES, Headers
from ..logger import get_logger
from ..types import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PaymentError,
    RateLimitError,
    ServerError,
    SnapPayError,
    ValidationError,
)
from ..utils import IdempotencyKeyGenerator, RetryHandler, sanitize_log_data


class BaseService:
    """Base service class with shared HTTP functionality.

    This class provides core HTTP request functionality with:
    - Automatic retry logic
    - Comprehensive error handling
    - Request/response logging
    - Rate limit handling
    - Pagination support
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        retry_config: Optional[Dict[str, Any]] = None,
        logger_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize service with shared session and configuration.

        Args:
            session: Shared aiohttp client session
            base_url: Base URL for API requests
            retry_config: Retry configuration options
            logger_config: Logger configuration options
        """
        self._session = session
        self.base_url = base_url

        # Initialize retry handler
        retry_config = retry_config or {}
        self._retry_handler = RetryHandler(
            max_retries=retry_config.get("max_retries", 3),
            base_delay=retry_config.get("base_delay", 1.0),
            max_delay=retry_config.get("max_delay", 60.0),
            jitter=retry_config.get("jitter", True),
        )

        # Initialize logger
        logger_config = logger_config or {}
        self._logger = get_logger("snappay.services", logger_config)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        idempotency_key: Optional[str] = None,
        retry: bool = True,
    ) -> Dict[str, Any]:
        """Make HTTP request to SnapPay API with comprehensive error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base_url, e.g., '/api/sdk/customer')
            data: Request body data (will be JSON encoded)
            params: URL query parameters
            timeout: Request timeout in seconds
            idempotency_key: Optional idempotency key for request
            retry: Whether to retry on failure

        Returns:
            Parsed JSON response as dictionary

        Raises:
            AuthenticationError: Invalid API key (401)
            NotFoundError: Resource not found (404)
            ValidationError: Invalid request data (400, 422)
            RateLimitError: Rate limit exceeded (429)
            ConflictError: Resource conflict (409)
            PaymentError: Payment processing failed
            ServerError: Server error (500+)
            SnapPayError: Other API errors
        """
        if retry:
            return await self._retry_handler.execute(
                self._execute_request,  # type: ignore[arg-type]
                method,
                endpoint,
                data,
                params,
                timeout,
                idempotency_key,
            )
        else:
            return await self._execute_request(
                method,
                endpoint,
                data,
                params,
                timeout,
                idempotency_key,
            )

    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a single HTTP request without retry.

        Internal method that performs the actual HTTP request.
        """
        # Construct full URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        headers = dict(self._session.headers or {})
        if idempotency_key:
            headers[Headers.IDEMPOTENCY_KEY] = idempotency_key

        # Prepare request kwargs
        kwargs: Dict[str, Any] = {
            "timeout": aiohttp.ClientTimeout(total=timeout),
            "params": params or {},
            "headers": headers,
        }

        # Add JSON data for methods that support body
        if data is not None and method.upper() in ("POST", "PUT", "PATCH"):
            kwargs["json"] = data

        # Log request
        start_time = time.time()
        self._logger.log_request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=data,
            params=params,
        )

        try:
            async with self._session.request(method, url, **kwargs) as response:
                duration = time.time() - start_time

                # Extract headers
                request_id = response.headers.get(
                    Headers.REQUEST_ID, response.headers.get("Request-ID")
                )
                retry_after = response.headers.get(Headers.RETRY_AFTER)

                # Read response body
                try:
                    response_data: Dict[str, Any] = await response.json()
                except (aiohttp.ContentTypeError, json.JSONDecodeError):
                    response_text = await response.text()
                    response_data = {"message": response_text or "Empty response"}

                # Log response
                self._logger.log_response(
                    status=response.status,
                    url=url,
                    headers=dict(response.headers),
                    data=response_data,
                    duration=duration,
                )

                # Handle success responses
                if 200 <= response.status < 300:
                    return response_data

                # Extract error details
                error_message = response_data.get(
                    "message", response_data.get("error", f"HTTP {response.status}")
                )
                error_code = response_data.get("code")
                error_details = response_data.get("details", {})
                error_param = response_data.get("param")

                # Prepare error kwargs
                error_kwargs = {
                    "status_code": response.status,
                    "error_code": error_code,
                    "request_id": request_id,
                    "details": error_details,
                }

                if retry_after:
                    try:
                        error_kwargs["retry_after"] = int(retry_after)
                    except ValueError:
                        pass

                self._logger.error(
                    f"API request failed: {response.status}",
                    status_code=response.status,
                    error_message=error_message,
                    error_code=error_code,
                    request_id=request_id,
                )

                # Map status codes to specific exceptions
                exception_class: type[SnapPayError]

                if response.status == 401:
                    exception_class = AuthenticationError
                elif response.status == 404:
                    exception_class = NotFoundError
                elif response.status in (400, 422):
                    exception_class = ValidationError
                    if error_param:
                        error_kwargs["details"]["param"] = error_param
                elif response.status == 409:
                    exception_class = ConflictError
                elif response.status == 429:
                    exception_class = RateLimitError
                elif response.status >= 500:
                    exception_class = ServerError
                elif error_code and "payment" in str(error_code).lower():
                    exception_class = PaymentError
                else:
                    exception_class = SnapPayError

                raise exception_class(error_message, **error_kwargs)

        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            self._logger.log_exception(
                e,
                context={
                    "method": method.upper(),
                    "url": url,
                    "duration_ms": f"{duration * 1000:.2f}",
                },
            )
            raise SnapPayError(f"Network error: {str(e)}")
        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            self._logger.log_exception(
                e,
                context={
                    "method": method.upper(),
                    "url": url,
                    "timeout": timeout,
                    "duration_ms": f"{duration * 1000:.2f}",
                },
            )
            raise SnapPayError(f"Request timeout after {timeout} seconds")

    async def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        max_items: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Helper method for paginated API endpoints.

        Args:
            endpoint: API endpoint
            params: Query parameters
            limit: Items per page
            max_items: Maximum total items to fetch

        Returns:
            List of all fetched items
        """
        items: List[Dict[str, Any]] = []
        params = params or {}
        params["limit"] = min(limit, 100)  # Cap at API max

        while True:
            response = await self._make_request("GET", endpoint, params=params)

            # Extract items from response
            page_items = response.get("data", [])
            items.extend(page_items)

            # Check if we've reached the maximum
            if max_items and len(items) >= max_items:
                items = items[:max_items]
                break

            # Check for more pages
            if not response.get("has_more", False):
                break

            # Get cursor for next page
            if page_items:
                params["starting_after"] = page_items[-1].get("id")
            else:
                break

        return items

    def _validate_required_params(self, **params) -> None:
        """Validate required parameters are provided and non-empty.

        Args:
            **params: Parameter name-value pairs to validate

        Raises:
            ValidationError: If any parameter is missing or empty
        """
        for param_name, param_value in params.items():
            if param_value is None:
                raise ValidationError(f"{param_name} is required")

            if isinstance(param_value, str) and not param_value.strip():
                raise ValidationError(f"{param_name} cannot be empty")

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and clean request parameters.

        Args:
            params: Raw parameters

        Returns:
            Sanitized parameters
        """
        sanitized = {}
        for key, value in params.items():
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            sanitized[key] = value

        return sanitized
