"""Usage service for SnapPay usage tracking."""

from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ..types import (
    GetUsageResponse,
    SnapPayError,
    TrackUsageResponse,
    ValidationError,
)
from .base import BaseService


class UsageService(BaseService):
    """Service for usage tracking and reporting."""

    async def track(
        self,
        customer_id: str,
        feature_id: str,
        usage: int,
        idempotency_key: Optional[str] = None,
    ) -> TrackUsageResponse:
        """Track usage for a metered feature.

        Args:
            customer_id: SnapPay customer ID
            feature_id: Feature ID to track usage for
            usage: Usage amount to report
            idempotency_key: Optional idempotency key for duplicate protection

        Returns:
            TrackUsageResponse object with tracking confirmation

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

        if not isinstance(usage, int) or usage < 0:
            raise ValidationError("usage parameter must be a non-negative integer")

        # Generate idempotency key if not provided
        if not idempotency_key or not idempotency_key.strip():
            idempotency_key = str(uuid4())

        # Build request data
        request_data = {
            "customer_id": customer_id.strip(),
            "feature_id": feature_id.strip(),
            "usage": usage,
            "idempotency_key": idempotency_key,
        }

        response_data = await self._make_request(
            method="POST", endpoint="/api/v1/sdk/track-usage", data=request_data
        )

        # Extract data from the API response format: {'success': True, 'data': {...}}
        if not response_data.get("success"):
            error_message = response_data.get("error", "API request failed")
            raise SnapPayError(f"API returned success=false: {error_message}")

        data = response_data.get("data", {})

        # Map API response fields to TrackUsageResponse model
        response: TrackUsageResponse = {
            "customer_id": customer_id,
            "feature_id": feature_id,
            "usage_recorded": data.get("usage_recorded", usage),
            "usage_total": data.get("usage_total", usage),
            "timestamp": data.get("timestamp", ""),
            "idempotency_key": idempotency_key,
        }

        return response

    async def get(self, customer_id: str, feature_id: str) -> List[GetUsageResponse]:
        """Get current usage details for a customer's feature.

        Args:
            customer_id: SnapPay customer ID
            feature_id: Feature ID to get usage for

        Returns:
            List of GetUsageResponse objects with current usage and limits

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

        # Build query parameters for POST request
        request_data: Dict[str, str] = {
            "customer_id": customer_id.strip(),
            "feature_id": feature_id.strip(),
        }

        response_data = await self._make_request(
            method="POST", endpoint="/api/v1/sdk/get-usage", data=request_data
        )

        # Handle response format
        data_list: List[Dict[str, Any]]
        if "data" in response_data:
            raw_data = response_data["data"]
            data_list = raw_data if isinstance(raw_data, list) else [raw_data]
        else:
            data_list = (
                response_data if isinstance(response_data, list) else [response_data]
            )

        # Map API response fields to GetUsageResponse model according to documentation
        result: List[GetUsageResponse] = []
        for item in data_list:
            result.append(
                {
                    "total_usage": item.get("total_usage", 0),
                    "product_id": item.get("product_id", ""),
                    "feature_id": item.get("feature_id", ""),
                    "remaining": item.get("remaining"),
                    "limit": item.get("limit"),
                    "next_reset_at": item.get("next_reset_at"),
                }
            )

        return result
