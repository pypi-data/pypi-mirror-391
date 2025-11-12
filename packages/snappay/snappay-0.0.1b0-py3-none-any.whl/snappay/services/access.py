"""Access service for SnapPay feature access management."""

from ..types import AccessCheck, SnapPayError, ValidationError
from .base import BaseService


class AccessService(BaseService):
    """Service for feature access management."""

    async def check(self, customer_id: str, feature_id: str) -> AccessCheck:
        """Check if customer has access to a specific feature.

        Args:
            customer_id: SnapPay customer ID
            feature_id: Feature/plan ID to check access for

        Returns:
            AccessCheck object with access status and usage info

        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid parameters
            SnapPayError: If API request fails
        """
        # Validate required parameters
        if not customer_id or not customer_id.strip():
            raise ValidationError("customer_id parameter cannot be empty or None")

        if not feature_id or not feature_id.strip():
            raise ValidationError("feature_id parameter cannot be empty or None")

        # Build request data
        request_data = {
            "customer_id": customer_id.strip(),
            "feature_id": feature_id.strip(),
        }

        response_data = await self._make_request(
            method="POST", endpoint="/api/v1/sdk/check-access", data=request_data
        )

        # Handle response format
        if "data" in response_data:
            data = response_data["data"]
        else:
            data = response_data

        # Map API response fields to AccessCheck model
        return {
            "has_access": data.get("has_access"),
            "feature_id": feature_id,
            "usage": data.get("usage", None),
            "allowance": data.get("allowance", None),
            "next_reset_at": data.get("next_reset_at", None),
        }
