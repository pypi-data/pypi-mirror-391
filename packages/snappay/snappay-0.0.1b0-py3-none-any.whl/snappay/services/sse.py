"""SSE (Server-Sent Events) client for real-time event handling.

This module handles real-time webhook events from SnapPay via SSE.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp_sse_client import client as sse_client  # type: ignore[import-untyped]
from constants import SDK_VERSION

from ..sse_types import SSEEvent, SSEEventType
from ..types import SnapPayError

logger = logging.getLogger(__name__)


class SSEClient:
    """Client for handling Server-Sent Events from SnapPay."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.snappay.dev",
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 5,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self._session: Optional[aiohttp.ClientSession] = None
        self._sse_task: Optional[asyncio.Task] = None
        self._event_handlers: Dict[str, list[Callable]] = {}
        self._last_event_id: Optional[str] = None
        self._running = False
        self._reconnect_attempts = 0

    async def __aenter__(self) -> "SSEClient":
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is initialized."""
        if self._session is None or self._session.closed:
            headers = {
                "X-API-Key": self.api_key,
                f"User-Agent": f"snappay-python/{SDK_VERSION}",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
            # Configure timeout and connection settings for SSE
            timeout = aiohttp.ClientTimeout(total=None, connect=30)
            connector = aiohttp.TCPConnector(
                keepalive_timeout=60,
                enable_cleanup_closed=True,
                force_close=False,
                limit_per_host=10,
            )
            self._session = aiohttp.ClientSession(
                headers=headers, timeout=timeout, connector=connector
            )

    async def close(self) -> None:
        """Close the SSE connection and cleanup resources."""
        self._running = False

        if self._sse_task and not self._sse_task.done():
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass

        if self._session and not self._session.closed:
            await self._session.close()

    def on(self, event_type: str, handler: Callable[[SSEEvent], None]) -> None:
        """Register an event handler for a specific event type.

        Args:
            event_type: The type of event to handle (e.g., "CONNECTION_ESTABLISHED", "SUBSCRIPTION_UPDATED")
            handler: Async or sync function to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def on_any(self, handler: Callable[[SSEEvent], None]) -> None:
        """Register a handler for all events.

        Args:
            handler: Async or sync function to handle any event
        """
        self.on("*", handler)

    async def _emit_event(self, event: SSEEvent) -> None:
        """Emit event to registered handlers.

        Filters out system events (heartbeat, connection_established) unless
        explicitly subscribed to.
        """
        # Handle HEARTBEAT events
        if event.type == SSEEventType.HEARTBEAT:
            logger.debug(f"Received heartbeat at {event.created_at}")
            if SSEEventType.HEARTBEAT in self._event_handlers:
                for handler in self._event_handlers[SSEEventType.HEARTBEAT]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in heartbeat handler: {e}")
            return  # Don't emit heartbeat to wildcard handlers

        # Handle CONNECTION_ESTABLISHED events
        if event.type == SSEEventType.CONNECTION_ESTABLISHED:
            logger.info(f"SSE connection established at {event.created_at}")
            if SSEEventType.CONNECTION_ESTABLISHED in self._event_handlers:
                for handler in self._event_handlers[
                    SSEEventType.CONNECTION_ESTABLISHED
                ]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in connection established handler: {e}")
            return  # Don't emit to wildcard handlers

        # Emit to specific event type handlers
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.type}: {e}")

        # Emit to wildcard handlers
        if "*" in self._event_handlers:
            for handler in self._event_handlers["*"]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in wildcard event handler: {e}")

    async def _connect_sse(self) -> AsyncGenerator[SSEEvent, None]:
        """Connect to SSE endpoint and yield events."""
        await self._ensure_session()

        url = urljoin(self.base_url, "/api/v1/sse/events")
        params = {}
        if self._last_event_id:
            params["last_event_id"] = self._last_event_id

        logger.info(f"Connecting to SSE endpoint: {url}")
        if self._last_event_id:
            logger.info(f"Resuming from last event ID: {self._last_event_id}")

        async with sse_client.EventSource(
            url,
            option={"method": "POST"},
            session=self._session,
            params=params,
            timeout=None,
            headers={
                "X-API-Key": self.api_key,
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        ) as event_source:
            async for event in event_source:
                if event.data:
                    try:
                        parsed_data = json.loads(event.data)

                        # Extract fields from SseEventData structure
                        event_id = parsed_data.get("id", "")
                        event_type = parsed_data.get("type", "")
                        event_data = parsed_data.get("data", {})
                        created_at = parsed_data.get("created_at", "")

                        sse_event = SSEEvent(
                            id=event_id,
                            type=event_type,
                            data=event_data,
                            created_at=created_at,
                        )

                        # Update last event ID for reconnection
                        if event_id:
                            self._last_event_id = event_id

                        # Reset reconnect attempts on successful event
                        self._reconnect_attempts = 0

                        yield sse_event

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse SSE event data: {e}")
                        logger.debug(f"Raw event data: {event.data}")
                    except Exception as e:
                        logger.error(f"Error processing SSE event: {e}")

    async def _run_sse_loop(self) -> None:
        """Main SSE event loop with reconnection logic."""
        while self._running:
            try:
                async for event in self._connect_sse():
                    if not self._running:
                        break
                    await self._emit_event(event)

            except asyncio.CancelledError:
                logger.info("SSE client cancelled")
                break

            except Exception as e:
                if not self._running:
                    break

                self._reconnect_attempts += 1

                if self._reconnect_attempts > self.max_reconnect_attempts:
                    logger.error(
                        f"Max reconnection attempts reached. Stopping SSE client."
                    )
                    self._running = False
                    break

                wait_time = min(self.reconnect_interval * self._reconnect_attempts, 60)
                logger.warning(
                    f"SSE connection error: {e}. Reconnecting in {wait_time} seconds..."
                )

                await asyncio.sleep(wait_time)

    async def start(self) -> None:
        """Start listening for SSE events."""
        if self._running:
            logger.warning("SSE client already running")
            return

        self._running = True
        self._reconnect_attempts = 0
        self._sse_task = asyncio.create_task(self._run_sse_loop())
        logger.info("SSE client started")

    async def stop(self) -> None:
        """Stop listening for SSE events."""
        if not self._running:
            logger.warning("SSE client not running")
            return

        self._running = False

        if self._sse_task and not self._sse_task.done():
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass

        logger.info("SSE client stopped")

    async def listen(
        self, include_system_events: bool = False
    ) -> AsyncGenerator[SSEEvent, None]:
        """Listen for SSE events and yield them.

        This is an alternative to using event handlers. You can use this
        in an async for loop to process events.

        Args:
            include_system_events: If True, include heartbeat and connection events.
                                 If False (default), filter them out.

        Yields:
            SSEEvent objects, excluding system events unless requested
        """
        await self._ensure_session()

        async for event in self._connect_sse():
            # Filter out system events unless explicitly requested
            if not include_system_events:
                if event.type in (
                    SSEEventType.HEARTBEAT,
                    SSEEventType.CONNECTION_ESTABLISHED,
                ):
                    # Log them but don't yield
                    if event.type == SSEEventType.HEARTBEAT:
                        logger.debug(f"Heartbeat received at {event.created_at}")
                    elif event.type == SSEEventType.CONNECTION_ESTABLISHED:
                        logger.info(f"Connection established at {event.created_at}")
                    continue

            yield event
