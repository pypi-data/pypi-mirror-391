"""Type definitions for SSE (Server-Sent Events) functionality.

This module provides type definitions specific to SSE event handling.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from snappay.types import BillingReason, PaymentStatus, SubscriptionStatus



@dataclass
class SubscriptionUpdatedData:
    """Data payload for SUBSCRIPTION_UPDATED SSE events.
    
    Supports dot notation access (data.customer_id) for better ergonomics.

    Attributes:
        customer_subscription_id: UUID of the customer subscription
        customer_id: UUID of the customer
        product_id: UUID of the product
        status: Subscription status enum (SubscriptionStatus.ACTIVE, etc.)
    """

    customer_subscription_id: Optional[str] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    status: Optional[SubscriptionStatus] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubscriptionUpdatedData":
        """Create instance from dictionary, parsing status string to enum."""
        status_str = data.get("status")
        status_enum = None
        if status_str:
            try:
                status_enum = SubscriptionStatus(status_str)
            except ValueError:
                # If status doesn't match enum, keep as None
                pass
        
        return cls(
            customer_subscription_id=data.get("customer_subscription_id"),
            customer_id=data.get("customer_id"),
            product_id=data.get("product_id"),
            status=status_enum,
        )


@dataclass
class PaymentUpdatedData:
    """Data payload for PAYMENT_UPDATED SSE events.
    
    Supports dot notation access (data.customer_id) for better ergonomics.

    Attributes:
        customer_subscription_id: UUID of the customer subscription
        customer_id: UUID of the customer
        product_id: UUID of the product
        status: Payment status enum (PaymentStatus.SUCCESS, etc.)
        reason: Optional reason for payment status
    """

    customer_subscription_id: Optional[str] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    status: Optional[PaymentStatus] = None
    reason: Optional[BillingReason] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentUpdatedData":
        """Create instance from dictionary, parsing status string to enum."""
        status_str = data.get("status")
        status_enum = None
        if status_str:
            try:
                status_enum = PaymentStatus(status_str)
            except ValueError:
                # If status doesn't match enum, keep as None
                pass
        
        reason_str = data.get("reason")
        reason_enum = None
        if reason_str:
            try:
                reason_enum = BillingReason(reason_str)
            except ValueError:
                # If reason doesn't match enum, keep as None
                pass
        
        return cls(
            customer_subscription_id=data.get("customer_subscription_id"),
            customer_id=data.get("customer_id"),
            product_id=data.get("product_id"),
            status=status_enum,
            reason=reason_enum,
        )

class SSEEventType:
    """SSE event types from the backend."""

    CONNECTION_ESTABLISHED = "CONNECTION_ESTABLISHED"
    HEARTBEAT = "HEARTBEAT"
    SUBSCRIPTION_UPDATED = "SUBSCRIPTION_UPDATED"
    PAYMENT_UPDATED = "PAYMENT_UPDATED"

class SSEEvent:
    """Represents an SSE event from SnapPay.

    Matches the backend SseEventData structure:
    - id: Event ID (UUID string)
    - type: Event type (CONNECTION_ESTABLISHED, HEARTBEAT, SUBSCRIPTION_UPDATED, PAYMENT_UPDATED)
    - data: Event data payload (dict)
    - createdAt: ISO timestamp string
    """

    def __init__(
        self,
        id: str,
        type: str,
        data: Dict[str, Any],
        created_at: str,
    ):
        self.id = id
        self.type = type
        self.data = data
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"SSEEvent(id={self.id}, type={self.type}, created_at={self.created_at})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "created_at": self.created_at,
        }

    @property
    def subscription_data(self) -> Optional[SubscriptionUpdatedData]:
        """Get subscription data for SUBSCRIPTION_UPDATED events.
        
        Returns typed SubscriptionUpdatedData with dot notation access.
        
        Example:
            >>> if event.subscription_data:
            >>>     print(event.subscription_data.customer_id)
            >>>     print(event.subscription_data.status)
        """
        if self.type == SSEEventType.SUBSCRIPTION_UPDATED:
            return SubscriptionUpdatedData.from_dict(self.data)
        return None

    @property
    def payment_data(self) -> Optional[PaymentUpdatedData]:
        """Get payment data for PAYMENT_UPDATED events.
        
        Returns typed PaymentUpdatedData with dot notation access.
        
        Example:
            >>> if event.payment_data:
            >>>     print(event.payment_data.customer_id)
            >>>     print(event.payment_data.status)
            >>>     print(event.payment_data.reason)
        """
        if self.type == SSEEventType.PAYMENT_UPDATED:
            return PaymentUpdatedData.from_dict(self.data)
        return None