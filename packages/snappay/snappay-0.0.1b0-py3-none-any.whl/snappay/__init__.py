"""SnapPay Python SDK

A modern, async Python SDK for integrating with SnapPay's payment
and subscription platform.
"""

from .client import SnapPay
from .config import SnapPayConfig
from .services.sse import SSEClient
from .sse_types import PaymentStatus, SSEEvent, SSEEventType, SubscriptionUpdatedData
from .types import (
    AccessCheck,
    AuthenticationError,
    CheckoutSession,
    ConflictError,
    Customer,
    GetUsageResponse,
    NotFoundError,
    PaymentError,
    Provider,
    RateLimitError,
    ServerError,
    SnapPayError,
    TrackUsageResponse,
    UsageResponse,
    ValidationError,
)

__all__ = [
    "SnapPay",
    "SnapPayConfig",
    "SSEClient",
    "SSEEvent",
    "SSEEventType",
    "Customer",
    "CheckoutSession",
    "AccessCheck",
    "GetUsageResponse",
    "UsageResponse",
    "TrackUsageResponse",
    "Provider",
    "PaymentStatus",
    "SubscriptionUpdatedData",
    "SnapPayError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "PaymentError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
