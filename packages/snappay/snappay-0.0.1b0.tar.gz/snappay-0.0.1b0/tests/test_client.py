"""Tests for SnapPay client initialization and configuration.

This module tests the main SnapPay client class including:
- Initialization with various configurations
- Context manager behavior
- Service property access
- Error handling
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from snappay import SnapPay, SnapPayConfig
from snappay.types import AuthenticationError


class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = SnapPay(api_key="pk_test_123")
        assert client.api_key == "pk_test_123"
        assert client.base_url == "https://api.snappay.dev"

    def test_init_with_config(self):
        """Test client initialization with config object."""
        config = SnapPayConfig(
            api_key="pk_test_456",
            base_url="https://api.example.com",
        )
        client = SnapPay(config=config)
        assert client.api_key == "pk_test_456"
        assert client.base_url == "https://api.example.com"

    def test_init_from_environment(self):
        """Test client initialization from environment variable."""
        with patch.dict(os.environ, {"SNAPPAY_API_KEY": "pk_test_789"}):
            client = SnapPay()
            assert client.api_key == "pk_test_789"

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                SnapPay()
            assert "API key must be provided" in str(exc_info.value)

    def test_init_with_invalid_api_key_format(self):
        """Test that invalid API key format raises error."""
        with pytest.raises(AuthenticationError) as exc_info:
            SnapPay(api_key="invalid_key")
        assert "Invalid API key format" in str(exc_info.value)

    def test_init_with_empty_api_key(self):
        """Test that empty API key raises error."""
        with pytest.raises(AuthenticationError) as exc_info:
            SnapPay(api_key="")
        assert "API key must be provided" in str(exc_info.value)

    def test_init_with_whitespace_api_key(self):
        """Test that whitespace-only API key raises error."""
        with pytest.raises(AuthenticationError) as exc_info:
            SnapPay(api_key="   ")
        assert "API key must be provided" in str(exc_info.value)

    def test_valid_api_key_formats(self):
        """Test that valid API key formats are accepted."""
        # Test key should work
        client_test = SnapPay(api_key="pk_test_abc123")
        assert client_test.api_key == "pk_test_abc123"

        # Live key should work
        client_live = SnapPay(api_key="pk_live_xyz789")
        assert client_live.api_key == "pk_live_xyz789"

    def test_base_url_normalization(self):
        """Test that base URL is normalized (trailing slash removed)."""
        client = SnapPay(
            api_key="pk_test_123",
            base_url="https://api.example.com/",
        )
        assert client.base_url == "https://api.example.com"


class TestClientContextManager:
    """Test client context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_session(self):
        """Test that context manager creates aiohttp session."""
        client = SnapPay(api_key="pk_test_123")
        assert client._session is None

        async with client:
            assert client._session is not None
            assert not client._session.closed

        # Session should be closed after exiting context
        assert client._session.closed

    @pytest.mark.asyncio
    async def test_context_manager_initializes_services(self):
        """Test that context manager initializes service instances."""
        client = SnapPay(api_key="pk_test_123")

        async with client:
            assert client._customers is not None
            assert client._checkout is not None
            assert client._access is not None
            assert client._usage is not None

    @pytest.mark.asyncio
    async def test_multiple_context_entries(self):
        """Test that client can be used in multiple context managers."""
        client = SnapPay(api_key="pk_test_123")

        # First context
        async with client:
            first_session = client._session
            assert not first_session.closed

        # Session closed after first context
        assert first_session.closed

        # Second context should create new session
        async with client:
            second_session = client._session
            assert second_session != first_session
            assert not second_session.closed

    @pytest.mark.asyncio
    async def test_explicit_close(self):
        """Test explicit close method."""
        client = SnapPay(api_key="pk_test_123")

        async with client:
            assert client._session is not None
            await client.close()
            assert client._session.closed


class TestServiceProperties:
    """Test service property access."""

    def test_service_access_without_session_raises_error(self):
        """Test that accessing services without session raises error."""
        client = SnapPay(api_key="pk_test_123")

        with pytest.raises(RuntimeError) as exc_info:
            _ = client.customers
        assert "Client session not initialized" in str(exc_info.value)

        with pytest.raises(RuntimeError) as exc_info:
            _ = client.checkout
        assert "Client session not initialized" in str(exc_info.value)

        with pytest.raises(RuntimeError) as exc_info:
            _ = client.access
        assert "Client session not initialized" in str(exc_info.value)

        with pytest.raises(RuntimeError) as exc_info:
            _ = client.usage
        assert "Client session not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_service_access_with_session(self):
        """Test that services are accessible with active session."""
        client = SnapPay(api_key="pk_test_123")

        async with client:
            assert client.customers is not None
            assert client.checkout is not None
            assert client.access is not None
            assert client.usage is not None

            # Services should be the same instance on repeated access
            customers1 = client.customers
            customers2 = client.customers
            assert customers1 is customers2


class TestConfigIntegration:
    """Test client integration with configuration."""

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "SNAPPAY_API_KEY": "pk_test_env",
                "SNAPPAY_BASE_URL": "https://api.env.com",
                "SNAPPAY_MAX_RETRIES": "5",
                "SNAPPAY_TIMEOUT": "60",
            },
        ):
            config = SnapPayConfig.from_env()
            assert config.api_key == "pk_test_env"
            assert config.base_url == "https://api.env.com"
            assert config.retry.max_retries == 5
            assert config.timeout.total == 60

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config should work
        config = SnapPayConfig(api_key="pk_test_123")
        assert config.api_key == "pk_test_123"

        # Invalid API key should raise error
        with pytest.raises(AuthenticationError) as exc_info:
            SnapPayConfig(api_key="invalid")
        assert "Invalid API key format" in str(exc_info.value)

    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = SnapPayConfig(
            api_key="pk_test_123",
            base_url="https://api.example.com",
        )
        config_dict = config.to_dict()

        # API key should be redacted
        assert config_dict["api_key"] == "***"
        assert config_dict["base_url"] == "https://api.example.com"
        assert "retry" in config_dict
        assert "timeout" in config_dict
