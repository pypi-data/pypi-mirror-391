"""SnapPay Python SDK Client.

Main client class for interacting with SnapPay's APIs with advanced features
including retry logic, configuration management, and SSE support.
"""

from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

import aiohttp

from .config import SnapPayConfig
from .services import AccessService, CheckoutService, CustomerService, UsageService
from .services.sse import SSEClient, SSEEvent
from .types import (
    AccessCheck,
    AuthenticationError,
    CheckoutSession,
    Customer,
    GetUsageResponse,
    Provider,
    TrackUsageResponse,
    UsageResponse,
)


class SnapPay:
    """SnapPay async client for Python applications.

    Provides methods for customer management, checkout sessions,
    access control, and usage tracking.

    Args:
        api_key: SnapPay API key (optional if using config or env var)
        base_url: Base URL for API (optional)
        config: SnapPayConfig instance (takes precedence over other args)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[SnapPayConfig] = None,
    ):
        """Initialize SnapPay client.

        Args:
            api_key: API key (optional if using config or env var)
            base_url: Base URL for API (optional)
            config: SnapPayConfig instance (takes precedence)
        """
        # Use provided config or create one from parameters
        if config:
            self.config = config
        else:
            self.config = SnapPayConfig(
                api_key=api_key,
                base_url=base_url or "https://api.snappay.dev",
            )

        # Extract commonly used values
        self.api_key = self.config.api_key
        self.base_url = self.config.base_url

        # Validate API key
        if not self.api_key or not self.api_key.strip():
            raise AuthenticationError(
                "API key must be provided either as parameter, "
                "in config, or via SNAPPAY_API_KEY environment variable"
            )

        # Validate API key format
        if not (
            self.api_key.startswith("pk_test_") or self.api_key.startswith("pk_live_")
        ):
            raise AuthenticationError(
                "Invalid API key format. API key must start with "
                "'pk_test_' or 'pk_live_'"
            )

        self._session: Optional[aiohttp.ClientSession] = None
        self._sse_client: Optional[SSEClient] = None

        # Initialize services (will be set up when session is created)
        self._customers: Optional[CustomerService] = None
        self._checkout: Optional[CheckoutService] = None
        self._access: Optional[AccessService] = None
        self._usage: Optional[UsageService] = None

    async def __aenter__(self) -> "SnapPay":
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is initialized."""
        if self._session is None or self._session.closed:
            assert self.api_key is not None  # Type assertion for mypy
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": self.config.user_agent,
            }

            # Add custom headers if provided
            headers.update(self.config.custom_headers)

            # Create timeout
            timeout = aiohttp.ClientTimeout(
                total=self.config.timeout.total,
                connect=self.config.timeout.connect,
                sock_connect=self.config.timeout.sock_connect,
                sock_read=self.config.timeout.sock_read,
            )

            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
            )

            # Prepare service configuration
            retry_config = {
                "max_retries": self.config.retry.max_retries,
                "base_delay": self.config.retry.base_delay,
                "max_delay": self.config.retry.max_delay,
                "jitter": self.config.retry.jitter,
            }

            logger_config = {
                "enabled": self.config.logging.enabled,
                "level": self.config.logging.level,
                "log_requests": self.config.logging.log_requests,
                "log_responses": self.config.logging.log_responses,
                "redact_sensitive": self.config.logging.redact_sensitive,
            }

            # Initialize services with the session and config
            self._customers = CustomerService(
                self._session, self.base_url, retry_config, logger_config
            )
            self._checkout = CheckoutService(
                self._session, self.base_url, retry_config, logger_config
            )
            self._access = AccessService(
                self._session, self.base_url, retry_config, logger_config
            )
            self._usage = UsageService(
                self._session, self.base_url, retry_config, logger_config
            )

    async def close(self) -> None:
        """Close the aiohttp session and SSE client."""
        if self._sse_client:
            await self._sse_client.close()
        if self._session and not self._session.closed:
            await self._session.close()

    @property
    def customers(self) -> CustomerService:
        """Get customer service instance."""
        if self._customers is None:
            raise RuntimeError(
                "Client session not initialized. Use async context manager or call _ensure_session()."
            )
        return self._customers

    @property
    def checkout(self) -> CheckoutService:
        """Get checkout service instance."""
        if self._checkout is None:
            raise RuntimeError(
                "Client session not initialized. Use async context manager or call _ensure_session()."
            )
        return self._checkout

    @property
    def access(self) -> AccessService:
        """Get access service instance."""
        if self._access is None:
            raise RuntimeError(
                "Client session not initialized. Use async context manager or call _ensure_session()."
            )
        return self._access

    @property
    def usage(self) -> UsageService:
        """Get usage service instance."""
        if self._usage is None:
            raise RuntimeError(
                "Client session not initialized. Use async context manager or call _ensure_session()."
            )
        return self._usage

    # SSE Event Streaming Methods

    def events(
        self,
        reconnect_interval: Optional[int] = None,
        max_reconnect_attempts: Optional[int] = None,
    ) -> SSEClient:
        """Get or create SSE client for real-time event streaming.

        Args:
            reconnect_interval: Seconds to wait between reconnection attempts
            max_reconnect_attempts: Maximum number of reconnection attempts

        Returns:
            SSEClient instance for managing event subscriptions

        Example:
            ```python
            async with SnapPay(api_key) as client:
                # Subscribe to events
                client.events().on("SUBSCRIPTION_UPDATED", handle_subscription_updated)
                client.events().on("CONNECTION_ESTABLISHED", handle_connection)

                # Start listening
                await client.start_events()

                # Keep running
                await asyncio.sleep(3600)  # Listen for 1 hour
            ```
        """
        if self._sse_client is None:
            assert self.api_key is not None  # Type assertion for mypy
            self._sse_client = SSEClient(
                api_key=self.api_key,
                base_url=self.base_url,
                reconnect_interval=reconnect_interval
                or self.config.sse.reconnect_interval,
                max_reconnect_attempts=max_reconnect_attempts
                or self.config.sse.max_reconnect_attempts,
            )
        return self._sse_client

    async def start_events(
        self,
        reconnect_interval: Optional[int] = None,
        max_reconnect_attempts: Optional[int] = None,
    ) -> None:
        """Start listening for real-time SSE events.

        Args:
            reconnect_interval: Seconds to wait between reconnection attempts
            max_reconnect_attempts: Maximum number of reconnection attempts

        Example:
            ```python
            async with SnapPay(api_key) as client:
                # Subscribe to events
                client.on_event(SSEEventType.SUBSCRIPTION_UPDATED, handle_subscription)

                # Start listening
                await client.start_events()

                # Keep running
                await asyncio.sleep(3600)
            ```
        """
        sse_client = self.events(
            reconnect_interval or self.config.sse.reconnect_interval,
            max_reconnect_attempts or self.config.sse.max_reconnect_attempts,
        )
        await sse_client.start()

    async def stop_events(self) -> None:
        """Stop listening for real-time SSE events."""
        if self._sse_client:
            await self._sse_client.stop()

    def on_event(
        self,
        event_type: str,
        handler: Callable[[SSEEvent], None],
    ) -> None:
        """Subscribe to a specific event type.

        Args:
            event_type: The type of event to handle (e.g., "SUBSCRIPTION_UPDATED", "CONNECTION_ESTABLISHED")
            handler: Async or sync function to handle the event

        Example:
            ```python
            def handle_subscription(event: SSEEvent):
                print(f"Event type: {event.type}")
                print(f"Event ID: {event.id}")
                print(f"Subscription data: {event.data}")

            client.on_event(SSEEventType.SUBSCRIPTION_UPDATED, handle_subscription)
            ```
        """
        self.events().on(event_type, handler)

    def on_any_event(self, handler: Callable[[SSEEvent], None]) -> None:
        """Subscribe to all events.

        Args:
            handler: Async or sync function to handle any event

        Example:
            ```python
            def handle_any_event(event: SSEEvent):
                print(f"Received event: {event.type}")

            client.on_any_event(handle_any_event)
            ```
        """
        self.events().on_any(handler)

    async def stream_events(
        self,
        reconnect_interval: Optional[int] = None,
        max_reconnect_attempts: Optional[int] = None,
        include_system_events: bool = False,
    ) -> AsyncGenerator[SSEEvent, None]:
        """Stream real-time events using async generator.

        This is an alternative to using event handlers. You can use this
        in an async for loop to process events.

        Args:
            reconnect_interval: Seconds to wait between reconnection attempts
            max_reconnect_attempts: Maximum number of reconnection attempts
            include_system_events: If True, include heartbeat and connection events

        Yields:
            SSEEvent objects as they are received (excluding system events by default)

        Example:
            ```python
            async with SnapPay(api_key) as client:
                async for event in client.stream_events():
                    print(f"Event: {event.type}")
                    print(f"Event ID: {event.id}")
                    print(f"Data: {event.data}")
            ```
        """
        sse_client = self.events(
            reconnect_interval or self.config.sse.reconnect_interval,
            max_reconnect_attempts or self.config.sse.max_reconnect_attempts,
        )
        async for event in sse_client.listen(include_system_events):
            yield event
