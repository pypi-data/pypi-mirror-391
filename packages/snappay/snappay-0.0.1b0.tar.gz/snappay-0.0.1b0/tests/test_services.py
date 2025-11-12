"""Tests for SnapPay service modules.

This module tests all service classes including:
- Customer service
- Checkout service
- Access service
- Usage service
"""

from unittest.mock import AsyncMock, patch

import pytest

from snappay.services.access import AccessService
from snappay.services.checkout import CheckoutService
from snappay.services.customers import CustomerService
from snappay.services.usage import UsageService
from snappay.types import NotFoundError, ValidationError


class TestCustomerService:
    """Test customer service functionality."""

    @pytest.mark.asyncio
    async def test_get_customer_success(self, mock_session):
        """Test successful customer retrieval/creation."""
        service = CustomerService(mock_session, "https://api.test.com")

        # Mock successful response
        service._make_request = AsyncMock(
            return_value={
                "data": {
                    "cus_id": "cus_123",
                    "email": "test@example.com",
                    "name": "Test User",
                }
            }
        )

        result = await service.get(
            "user_123",
            email="test@example.com",
            name="Test User",
        )

        assert result["customer_id"] == "cus_123"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        service._make_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customer_invalid_email(self, mock_session):
        """Test get_customer with invalid email."""
        service = CustomerService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError) as exc_info:
            await service.get("user_123", email="invalid-email")
        assert "Invalid email format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_customer_empty_cusid(self, mock_session):
        """Test get_customer with empty cusId."""
        service = CustomerService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError) as exc_info:
            await service.get("", email="test@example.com")
        assert "customer_id cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_customer_response_without_data_wrapper(self, mock_session):
        """Test get_customer when response doesn't have 'data' wrapper."""
        service = CustomerService(mock_session, "https://api.test.com")

        # Response without 'data' wrapper
        service._make_request = AsyncMock(
            return_value={
                "cus_id": "cus_123",
                "email": "test@example.com",
                "name": "Test User",
            }
        )

        result = await service.get("user_123", email="test@example.com")
        assert result["customer_id"] == "cus_123"
        assert result["email"] == "test@example.com"


class TestCheckoutService:
    """Test checkout service functionality."""

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(self, mock_session):
        """Test successful checkout session creation."""
        service = CheckoutService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "data": {
                    "session_id": "cs_123",
                    "url": "https://checkout.stripe.com/pay/cs_123",
                    "expires_at": "2024-01-01T01:00:00Z",
                }
            }
        )

        result = await service.create_session(
            customer_id="cus_123",
            product_id="prod_123",
            success_url="https://example.com/success",
        )

        assert result["session_id"] == "cs_123"
        assert "checkout.stripe.com" in result["url"]
        service._make_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_checkout_invalid_urls(self, mock_session):
        """Test checkout session creation with invalid URLs."""
        service = CheckoutService(mock_session, "https://api.test.com")

        # Invalid success URL
        with pytest.raises(ValidationError) as exc_info:
            await service.create_session(
                customer_id="cus_123",
                product_id="prod_123",
                success_url="not-a-url",
            )
        assert "Invalid success URL" in str(exc_info.value)

        # Invalid cancel URL
        with pytest.raises(ValidationError) as exc_info:
            await service.create_session(
                customer_id="cus_123",
                product_id="prod_123",
                success_url="https://example.com/success",
                cancel_url="not-a-url",
            )
        assert "Invalid cancel URL" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_checkout_empty_params(self, mock_session):
        """Test checkout session creation with empty parameters."""
        service = CheckoutService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError):
            await service.create_session(
                customer_id="",
                product_id="prod_123",
                success_url="https://example.com",
            )

        with pytest.raises(ValidationError):
            await service.create_session(
                customer_id="cus_123",
                product_id="",
                success_url="https://example.com",
            )


class TestAccessService:
    """Test access service functionality."""

    @pytest.mark.asyncio
    async def test_check_access_granted(self, mock_session):
        """Test access check when access is granted."""
        service = AccessService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "data": {
                    "has_access": True,
                    "usage": 50,
                    "allowance": 100,
                    "next_reset_at": "1690000000000",
                }
            }
        )

        result = await service.check("cus_123", "feature_123")
        assert result["has_access"] is True
        assert result["usage"] == 50
        assert result["allowance"] == 100
        assert result["feature_id"] == "feature_123"

    @pytest.mark.asyncio
    async def test_check_access_denied(self, mock_session):
        """Test access check when access is denied."""
        service = AccessService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "data": {
                    "has_access": False,
                    "remaining": 0,
                }
            }
        )

        result = await service.check("cus_123", "feature_123")
        assert result["has_access"] is False

    @pytest.mark.asyncio
    async def test_check_access_empty_params(self, mock_session):
        """Test access check with empty parameters."""
        service = AccessService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError):
            await service.check("", "feature_123")

        with pytest.raises(ValidationError):
            await service.check("cus_123", "")


class TestUsageService:
    """Test usage service functionality."""

    @pytest.mark.asyncio
    async def test_track_usage_success(self, mock_session):
        """Test successful usage tracking."""
        service = UsageService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "usage_recorded": 10,
                    "usage_total": 60,
                    "timestamp": "2024-01-01T00:00:00Z",
                },
            }
        )

        result = await service.track(
            customer_id="cus_123",
            feature_id="feature_123",
            usage=10,
        )

        assert result["usage_recorded"] == 10
        assert result["usage_total"] == 60

    @pytest.mark.asyncio
    async def test_track_usage_with_idempotency_key(self, mock_session):
        """Test usage tracking with idempotency key."""
        service = UsageService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "usage_recorded": 10,
                    "idempotency_key": "key_123",
                },
            }
        )

        result = await service.track(
            customer_id="cus_123",
            feature_id="feature_123",
            usage=10,
            idempotency_key="key_123",
        )

        assert result["idempotency_key"] == "key_123"

    @pytest.mark.asyncio
    async def test_track_usage_negative_amount(self, mock_session):
        """Test usage tracking with negative amount."""
        service = UsageService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError) as exc_info:
            await service.track(
                customer_id="cus_123",
                feature_id="feature_123",
                usage=-10,
            )
        assert "usage parameter must be a non-negative integer" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_usage_success(self, mock_session):
        """Test successful usage retrieval."""
        service = UsageService(mock_session, "https://api.test.com")

        service._make_request = AsyncMock(
            return_value={
                "data": [
                    {
                        "total_usage": 250,
                        "product_id": "prod_123",
                        "feature_id": "feature_123",
                        "remaining": 750,
                        "limit": 1000,
                        "next_reset_at": "1690000000000",
                    }
                ]
            }
        )

        result = await service.get("cus_123", "feature_123")
        assert isinstance(result, list)
        assert len(result) == 1
        item = result[0]
        assert item["limit"] == 1000
        assert item["total_usage"] == 250
        assert item["remaining"] == 750
        assert item["product_id"] == "prod_123"
        assert item["feature_id"] == "feature_123"

    @pytest.mark.asyncio
    async def test_get_usage_empty_params(self, mock_session):
        """Test get with empty parameters."""
        service = UsageService(mock_session, "https://api.test.com")

        with pytest.raises(ValidationError):
            await service.get("", "feature_123")

        with pytest.raises(ValidationError):
            await service.get("cus_123", "")


class TestBaseServiceFunctionality:
    """Test base service shared functionality."""

    @pytest.mark.asyncio
    async def test_pagination_helper(self, mock_session):
        """Test pagination helper method."""
        service = CustomerService(mock_session, "https://api.test.com")

        # Mock paginated responses
        page1_response = {
            "data": [{"id": "1"}, {"id": "2"}],
            "has_more": True,
        }
        page2_response = {
            "data": [{"id": "3"}, {"id": "4"}],
            "has_more": False,
        }

        service._make_request = AsyncMock(side_effect=[page1_response, page2_response])

        result = await service._paginate("/endpoint", limit=2)
        assert len(result) == 4
        assert result[0]["id"] == "1"
        assert result[-1]["id"] == "4"

    @pytest.mark.asyncio
    async def test_pagination_with_max_items(self, mock_session):
        """Test pagination with max_items limit."""
        service = CustomerService(mock_session, "https://api.test.com")

        response = {
            "data": [{"id": str(i)} for i in range(10)],
            "has_more": True,
        }

        service._make_request = AsyncMock(return_value=response)

        result = await service._paginate("/endpoint", max_items=5)
        assert len(result) == 5

    def test_validate_required_params(self, mock_session):
        """Test parameter validation helper."""
        service = CustomerService(mock_session, "https://api.test.com")

        # Valid params should pass
        service._validate_required_params(param1="value1", param2="value2")

        # None params should raise error
        with pytest.raises(ValidationError) as exc_info:
            service._validate_required_params(param1=None)
        assert "param1 is required" in str(exc_info.value)

        # Empty string params should raise error
        with pytest.raises(ValidationError) as exc_info:
            service._validate_required_params(param1="   ")
        assert "param1 cannot be empty" in str(exc_info.value)

    def test_sanitize_params(self, mock_session):
        """Test parameter sanitization helper."""
        service = CustomerService(mock_session, "https://api.test.com")

        params = {
            "good": "value",
            "empty": "",
            "whitespace": "   ",
            "none": None,
            "trimmed": "  value  ",
        }

        result = service._sanitize_params(params)

        assert "good" in result
        assert result["good"] == "value"
        assert "empty" not in result
        assert "whitespace" not in result
        assert "none" not in result
        assert result["trimmed"] == "value"
