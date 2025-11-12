"""Customer service for SnapPay SDK.

This module provides customer management functionality for creating
and retrieving customer records.
"""

from typing import Any, Dict, Optional

from ..constants import Endpoints
from ..logger import log_method_call
from ..types import (
    CreateCustomerRequest,
    Customer,
    SnapPayError,
    ValidationError,
)
from ..utils import Validator
from .base import BaseService


class CustomerService(BaseService):
    """Service for customer management.

    Provides methods for creating and retrieving customer records in SnapPay.
    """

    @log_method_call
    async def get(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Customer:
        """Retrieve or create a customer record.

        This method will either retrieve an existing customer or create a new one
        if the customer doesn't exist. The customer_id is used as a unique identifier.

        Args:
            customer_id: Unique customer identifier (your internal ID)
            email: Customer email address
            name: Optional customer full name

        Returns:
            Customer object with all customer details

        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid parameters (empty customer_id, invalid email)
            SnapPayError: If API request fails

        Example:
            >>> customer = await client.customers.get(
            ...     customer_id="user_123",
            ...     email="john@example.com",
            ...     name="John Doe",
            ... )
        """
        # Validate required parameters
        self._validate_required_params(customer_id=customer_id)

        # Validate email format
        if email and not Validator.validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")

        # Build request data
        request_data: CreateCustomerRequest = {"cusId": customer_id.strip()}

        # Add optional fields
        if email:
            request_data["email"] = email.strip()
        if name:
            request_data["name"] = name.strip()

        # Make API request
        response_data = await self._make_request(
            method="POST",
            endpoint=Endpoints.CUSTOMER,
            data=dict(request_data),
        )

        # Handle response format
        if "data" in response_data:
            data = response_data["data"]
        else:
            data = response_data

        # Map API response to Customer type
        customer: Customer = {
            "customer_id": data.get("cus_id", data.get("customer_id", "")),
            "email": data.get("email", ""),
            "name": data.get("name"),
        }

        return customer
