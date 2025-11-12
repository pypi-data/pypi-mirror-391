"""Constants used throughout the SnapPay SDK.

This module defines all constant values used across the SDK including
API endpoints, default configurations, and status codes.
"""

# API Configuration
DEFAULT_BASE_URL = "https://api.snappay.dev"
API_VERSION = "v1"
SDK_VERSION = "0.0.1-beta"

# Timeout Settings (in seconds)
DEFAULT_TIMEOUT = 30
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_READ_TIMEOUT = 20

# Retry Configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_MAX_RETRY_DELAY = 60.0

# SSE Configuration
DEFAULT_RECONNECT_INTERVAL = 5
DEFAULT_RECONNECT_ATTEMPTS = 10
DEFAULT_HEARTBEAT_INTERVAL = 30

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# Retryable Status Codes
RETRYABLE_STATUS_CODES = {
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_ERROR,
    HTTP_SERVICE_UNAVAILABLE,
    502,  # Bad Gateway
    504,  # Gateway Timeout
}


# API Endpoints
class Endpoints:
    """API endpoint paths."""

    # Customer endpoints
    CUSTOMER = "/api/v1/sdk/customer"
    CUSTOMER_BY_ID = "/api/v1/sdk/customer/{customer_id}"

    # Checkout endpoints
    CHECKOUT_SESSION = "/api/v1/sdk/checkout/session"
    CHECKOUT_SESSION_BY_ID = "/api/v1/sdk/checkout/session/{session_id}"

    # Access control endpoints
    CHECK_ACCESS = "/api/v1/sdk/check-access"
    GRANT_ACCESS = "/api/v1/sdk/grant-access"
    REVOKE_ACCESS = "/api/v1/sdk/revoke-access"

    # Usage tracking endpoints
    TRACK_USAGE = "/api/v1/sdk/track-usage"
    GET_USAGE = "/api/v1/sdk/usage"
    RESET_USAGE = "/api/v1/sdk/reset-usage"

    # SSE streaming endpoint
    SSE_EVENTS = "/api/v1/sdk/events"

    # Billing endpoints
    SUBSCRIPTIONS = "/api/v1/sdk/subscriptions"
    SUBSCRIPTION_BY_ID = "/api/v1/sdk/subscriptions/{subscription_id}"
    INVOICES = "/api/v1/sdk/invoices"
    INVOICE_BY_ID = "/api/v1/sdk/invoices/{invoice_id}"

    # Product endpoints
    PRODUCTS = "/api/v1/sdk/products"
    PRODUCT_BY_ID = "/api/v1/sdk/products/{product_id}"
    PLANS = "/api/v1/sdk/plans"
    PLAN_BY_ID = "/api/v1/sdk/plans/{plan_id}"

    # Webhook endpoints
    WEBHOOK_EVENTS = "/api/v1/sdk/webhook-events"
    WEBHOOK_EVENT_BY_ID = "/api/v1/sdk/webhook-events/{event_id}"


# Event Types
class EventTypes:
    """SSE and webhook event types."""

    # Connection events
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_LOST = "connection.lost"
    HEARTBEAT = "heartbeat"

    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"

    # Subscription events
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_EXPIRED = "subscription.expired"
    SUBSCRIPTION_RENEWED = "subscription.renewed"

    # Payment events
    PAYMENT_INTENT_CREATED = "payment_intent.created"
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_FAILED = "payment_intent.failed"
    PAYMENT_METHOD_ATTACHED = "payment_method.attached"
    PAYMENT_METHOD_DETACHED = "payment_method.detached"

    # Invoice events
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_SUCCEEDED = "invoice.payment.succeeded"
    INVOICE_PAYMENT_FAILED = "invoice.payment.failed"
    INVOICE_OVERDUE = "invoice.overdue"

    # Usage events
    USAGE_RECORD_CREATED = "usage_record.created"
    USAGE_LIMIT_REACHED = "usage_limit.reached"
    USAGE_RESET = "usage.reset"

    # Checkout events
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
    CHECKOUT_SESSION_EXPIRED = "checkout.session.expired"


# Headers
class Headers:
    """HTTP header names."""

    API_KEY = "X-API-Key"
    CONTENT_TYPE = "Content-Type"
    USER_AGENT = "User-Agent"
    IDEMPOTENCY_KEY = "Idempotency-Key"
    REQUEST_ID = "X-Request-ID"
    RETRY_AFTER = "Retry-After"
    LAST_EVENT_ID = "Last-Event-ID"


# Content Types
class ContentTypes:
    """HTTP content type values."""

    JSON = "application/json"
    TEXT = "text/plain"
    FORM = "application/x-www-form-urlencoded"
    SSE = "text/event-stream"


# Error Codes
class ErrorCodes:
    """API error codes."""

    # Authentication errors
    INVALID_API_KEY = "invalid_api_key"
    EXPIRED_API_KEY = "expired_api_key"
    MISSING_API_KEY = "missing_api_key"

    # Validation errors
    INVALID_PARAMETER = "invalid_parameter"
    MISSING_PARAMETER = "missing_parameter"
    PARAMETER_TOO_LONG = "parameter_too_long"
    PARAMETER_TOO_SHORT = "parameter_too_short"

    # Resource errors
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_ALREADY_EXISTS = "resource_already_exists"
    RESOURCE_CONFLICT = "resource_conflict"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Server errors
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

    # Business logic errors
    INSUFFICIENT_FUNDS = "insufficient_funds"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_INACTIVE = "subscription_inactive"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    ACCESS_DENIED = "access_denied"


# Limits
class Limits:
    """SDK and API limits."""

    MAX_BATCH_SIZE = 100
    MAX_PAGE_SIZE = 100
    MAX_IDEMPOTENCY_KEY_LENGTH = 255
    MAX_CUSTOMER_ID_LENGTH = 255
    MAX_METADATA_SIZE = 16384  # 16KB
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_NAME_LENGTH = 255


# Defaults
class Defaults:
    """Default values for optional parameters."""

    PAGE_SIZE = 20
    BATCH_SIZE = 10
    CURRENCY = "usd"
    LOCALE = "en"
    TIMEZONE = "UTC"
