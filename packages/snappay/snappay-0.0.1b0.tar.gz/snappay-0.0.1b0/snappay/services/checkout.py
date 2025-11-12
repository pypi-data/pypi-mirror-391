"""Checkout service for SnapPay payment processing."""

from typing import Any, Optional

from snappay.utils import Validator

from ..types import CheckoutSession, CreateCheckoutRequest, Provider, SnapPayError, ValidationError
from .base import BaseService


class CheckoutService(BaseService):
    """Service for checkout session management."""

    async def create_session(
        self,
        customer_id: str,
        product_id: str,
        success_url: str,
        price_id: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> CheckoutSession:
        """Create a Checkout Session URL.

        Args:
            customer_id: SnapPay customer ID
            product_id: Product/plan ID to purchase
            success_url: URL to redirect after successful payment
            price_id: Optional price ID to purchase
            cancel_url: Optional URL to redirect after cancelled payment

        Returns:
            CheckoutSession object with session URL, session ID, and expiration

        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid parameters
            SnapPayError: If API request fails
        """
        # Validate required parameters
        self._validate_required_params(customer_id=customer_id, product_id=product_id, success_url=success_url)

        # Validate URLs
        if not Validator.validate_url(success_url):
            raise ValidationError(f"Invalid success URL: {success_url}")

        if cancel_url and not Validator.validate_url(cancel_url):
            raise ValidationError(f"Invalid cancel URL: {cancel_url}")  

        # Build request data
        request_data: CreateCheckoutRequest = {
            "customer_id": customer_id.strip(),
            "product_id": product_id.strip(),
            "success_url": success_url.strip(),
        }

        # Add cancel_url if provided
        if cancel_url and cancel_url.strip():
            request_data["cancel_url"] = cancel_url.strip()

        if price_id and price_id.strip():
            request_data["price_id"] = price_id.strip()

        response_data = await self._make_request(
            method="POST", endpoint="/api/v1/sdk/checkout-session", data=request_data
        )

        # Handle response format
        if "data" in response_data:
            data = response_data["data"]
        else:
            data = response_data

        # Map API response fields to CheckoutSession model
        return {
            "url": data.get("url", ""),
            "session_id": data.get("session_id", ""),
            "expires_at": data.get("expires_at", ""),
        }
