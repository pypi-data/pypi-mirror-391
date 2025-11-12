"""Type definitions for SnapPay Python SDK.

This module provides comprehensive type definitions for all API requests
and responses, ensuring type safety throughout the SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


class Provider(Enum):
    """Supported payment provider options."""

    STRIPE = "stripe"
    # PAYPAL = "paypal"
    # PADDLE = "paddle"
    # LEMONSQUEEZY = "lemonsqueezy"


class SubscriptionStatus(Enum):
    """Subscription status values."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    UNPAID = "UNPAID"
    TRIALING = "TRIALING"
    PAUSED = "PAUSED"

class PaymentStatus(Enum):
    """Payment status values for subscription events."""

    SUCCESS = "SUCCESS"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    FAILED = "FAILED"
    SUBSCRIPTION_RENEWED = "SUBSCRIPTION_RENEWED"

class BillingReason(Enum):
    """Billing reason values for payment events."""

    SUBSCRIPTION_CREATE = "SUBSCRIPTION_CREATE"
    SUBSCRIPTION_CYCLE = "SUBSCRIPTION_CYCLE"
    SUBSCRIPTION_UPDATE = "SUBSCRIPTION_UPDATE"
    SUBSCRIPTION_THRESHOLD = "SUBSCRIPTION_THRESHOLD"
    MANUAL = "MANUAL"

class InvoiceStatus(Enum):
    """Invoice status values."""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Currency(Enum):
    """Supported currency codes."""

    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    JPY = "jpy"
    AUD = "aud"
    CAD = "cad"
    CHF = "chf"
    CNY = "cny"
    SEK = "sek"
    NZD = "nzd"


class Customer(TypedDict, total=False):
    """Customer record from SnapPay API.

    Attributes:
        customer_id: Unique customer identifier
        email: Customer email address
        name: Customer full name
    """

    customer_id: str
    email: str
    name: Optional[str]


class CheckoutSession(TypedDict, total=False):
    """Checkout session response.

    Attributes:
        session_id: Unique session identifier
        url: Checkout URL for customer
        expires_at: Session expiration timestamp
    """

    session_id: str
    url: str
    expires_at: str


class AccessCheck(TypedDict, total=False):
    """Feature access check response.

    Attributes:
        has_access: Whether customer has access
        feature_id: Feature being checked
        usage: Total usage recorded (null if has no access)
        allowance: Maximum usage allowed (null if has no access or is Boolean/Unlimited feature)
        next_reset_at: Next reset date (null if has no access or is Boolean/Unlimited feature)
    """

    has_access: bool
    feature_id: str
    usage: Optional[int]
    allowance: Optional[int]
    next_reset_at: Optional[str]


class UsageResponse(TypedDict, total=False):
    """Detailed usage information for a feature.

    Attributes:
        customer_id: Customer identifier
        feature_id: Feature identifier
        usage_total: Total usage recorded
        usage_remaining: Remaining usage available
        usage_limit: Maximum usage allowed
        reset_date: Next reset date
        last_updated: Last update timestamp
        period_start: Current period start
        period_end: Current period end
        overage_allowed: Whether overage is permitted
    """

    customer_id: str
    feature_id: str
    usage_total: int
    usage_remaining: Optional[int]
    usage_limit: Optional[int]
    reset_date: Optional[str]
    last_updated: str
    period_start: Optional[str]
    period_end: Optional[str]
    overage_allowed: Optional[bool]


class GetUsageResponse(TypedDict, total=False):
    """Response from get_usage API endpoint.

    Attributes:
        total_usage: Total usage recorded
        product_id: Product identifier (UUID)
        feature_id: Feature identifier (UUID)
        remaining: Remaining usage available
        limit: Usage limit for the feature
        next_reset_at: Next reset date
    """

    total_usage: int
    product_id: str
    feature_id: str
    remaining: Optional[int]
    limit: Optional[int]
    next_reset_at: Optional[str]


class TrackUsageResponse(TypedDict, total=False):
    """Response from track_usage API endpoint.

    Attributes:
        success: Whether tracking was successful
        customer_id: Customer identifier
        feature_id: Feature identifier
        usage_recorded: Amount recorded in this request
        usage_total: New total usage
        timestamp: Recording timestamp
        idempotency_key: Idempotency key used
    """

    customer_id: str
    feature_id: str
    usage_recorded: int
    usage_total: int
    timestamp: str
    idempotency_key: Optional[str]


class ErrorResponse(TypedDict, total=False):
    """Error response from SnapPay API.

    Attributes:
        error: Error type/category
        message: Human-readable error message
        code: Machine-readable error code
        request_id: Request identifier for debugging
        details: Additional error details
        param: Parameter that caused the error
    """

    error: str
    message: str
    code: str
    request_id: Optional[str]
    details: Optional[Dict[str, Any]]
    param: Optional[str]


# Additional type definitions for comprehensive API coverage


class Subscription(TypedDict, total=False):
    """Subscription record.

    Attributes:
        subscription_id: Unique subscription identifier
        customer_id: Associated customer
        product_id: Subscribed product
        plan_id: Specific plan within product
        status: Current subscription status
        current_period_start: Current billing period start
        current_period_end: Current billing period end
        created_at: Creation timestamp
        canceled_at: Cancellation timestamp (if applicable)
        trial_end: Trial period end (if applicable)
        metadata: Custom metadata
    """

    subscription_id: str
    customer_id: str
    product_id: str
    plan_id: str
    status: str
    current_period_start: str
    current_period_end: str
    created_at: str
    canceled_at: Optional[str]
    trial_end: Optional[str]
    metadata: Optional[Dict[str, Any]]


class Invoice(TypedDict, total=False):
    """Invoice record.

    Attributes:
        invoice_id: Unique invoice identifier
        customer_id: Associated customer
        subscription_id: Associated subscription
        amount_due: Amount due in cents
        amount_paid: Amount paid in cents
        currency: Invoice currency
        status: Current invoice status
        due_date: Payment due date
        paid_at: Payment timestamp (if paid)
        created_at: Creation timestamp
        lines: Invoice line items
    """

    invoice_id: str
    customer_id: str
    subscription_id: Optional[str]
    amount_due: int
    amount_paid: int
    currency: str
    status: str
    due_date: Optional[str]
    paid_at: Optional[str]
    created_at: str
    lines: Optional[List[Dict[str, Any]]]


class Product(TypedDict, total=False):
    """Product record.

    Attributes:
        product_id: Unique product identifier
        name: Product name
        description: Product description
        active: Whether product is active
        features: List of included features
        metadata: Custom metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    product_id: str
    name: str
    description: Optional[str]
    active: bool
    features: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class Plan(TypedDict, total=False):
    """Pricing plan record.

    Attributes:
        plan_id: Unique plan identifier
        product_id: Associated product
        name: Plan name
        amount: Price in cents
        currency: Plan currency
        interval: Billing interval (month/year)
        interval_count: Number of intervals
        trial_period_days: Trial period length
        active: Whether plan is active
        metadata: Custom metadata
    """

    plan_id: str
    product_id: str
    name: str
    amount: int
    currency: str
    interval: Literal["day", "week", "month", "year"]
    interval_count: int
    trial_period_days: Optional[int]
    active: bool
    metadata: Optional[Dict[str, Any]]


class WebhookEvent(TypedDict, total=False):
    """Webhook event record.

    Attributes:
        event_id: Unique event identifier
        event_type: Type of event
        created_at: Event timestamp
        data: Event payload
        request_id: Associated request ID
        attempts: Delivery attempt count
    """

    event_id: str
    event_type: str
    created_at: str
    data: Dict[str, Any]
    request_id: Optional[str]
    attempts: int


# Request type definitions


class CreateCustomerRequest(TypedDict, total=False):
    """Request to create or get a customer."""
    cusId: str
    email: Optional[str]
    name: Optional[str]


class CreateCheckoutRequest(TypedDict, total=False):
    """Request to create a checkout session."""

    customer_id: str
    product_id: str
    success_url: str
    cancel_url: Optional[str]
    price_id: Optional[str]


class CheckAccessRequest(TypedDict, total=False):
    """Request to check feature access."""

    customer_id: str
    feature_id: str


class TrackUsageRequest(TypedDict, total=False):
    """Request to track usage."""

    customer_id: str
    feature_id: str
    usage: int
    idempotency_key: Optional[str]
    timestamp: Optional[str]


# Pagination support


class PaginationParams(TypedDict, total=False):
    """Pagination parameters for list endpoints."""

    limit: int
    starting_after: Optional[str]
    ending_before: Optional[str]


class PaginatedResponse(TypedDict, total=False):
    """Paginated response wrapper."""

    data: List[Dict[str, Any]]
    has_more: bool
    total_count: Optional[int]
    next_cursor: Optional[str]
    previous_cursor: Optional[str]


class SnapPayError(Exception):
    """Base exception for SnapPay SDK errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (if applicable)
        error_code: Machine-readable error code
        request_id: Request ID for debugging
        retry_after: Seconds to wait before retry (for rate limits)
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.retry_after = retry_after
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"(Status: {self.status_code})")
        if self.error_code:
            parts.append(f"[Code: {self.error_code}]")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "status_code": self.status_code,
            "error_code": self.error_code,
            "request_id": self.request_id,
            "retry_after": self.retry_after,
            "details": self.details,
        }


class AuthenticationError(SnapPayError):
    """Raised when API key is invalid or missing.

    This error indicates authentication issues such as:
    - Invalid API key format
    - Expired API key
    - Missing API key
    - Insufficient permissions
    """


class RateLimitError(SnapPayError):
    """Raised when API rate limit is exceeded.

    Check the retry_after attribute for how long to wait
    before making another request.
    """


class NotFoundError(SnapPayError):
    """Raised when requested resource is not found.

    This error indicates the requested resource (customer,
    subscription, etc.) does not exist.
    """


class ValidationError(SnapPayError):
    """Raised when request parameters are invalid.

    Check the error details for specific validation failures.
    The 'param' attribute may indicate which parameter failed.
    """


class ConflictError(SnapPayError):
    """Raised when there's a resource conflict.

    This error indicates operations like:
    - Duplicate resource creation
    - Concurrent modification conflicts
    """


class PaymentError(SnapPayError):
    """Raised when payment processing fails.

    This error indicates payment-specific issues like:
    - Declined cards
    - Insufficient funds
    - Invalid payment methods
    """


class ServerError(SnapPayError):
    """Raised when server encounters an internal error.

    These errors are typically temporary and requests
    should be retried with exponential backoff.
    """
