"""Configuration module for SnapPay SDK.

This module provides configuration management for the SDK including
API settings, retry policies, timeouts, and other client options.
"""

import os
from constants import SDK_VERSION
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RECONNECT_ATTEMPTS,
    DEFAULT_RECONNECT_INTERVAL,
    DEFAULT_TIMEOUT,
)
from .types import AuthenticationError


@dataclass
class RetryConfig:
    """Configuration for retry logic with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds between retries (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        jitter: Whether to add jitter to retry delays (default: True)
    """

    max_retries: int = DEFAULT_MAX_RETRIES
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class TimeoutConfig:
    """Configuration for request timeouts.

    Attributes:
        total: Total timeout for the entire request in seconds (default: 30)
        connect: Timeout for establishing connection in seconds (default: 10)
        sock_read: Timeout for reading data from socket (default: 10)
        sock_connect: Timeout for socket connection (default: 10)
    """

    total: int = DEFAULT_TIMEOUT
    connect: int = 10
    sock_read: int = 10
    sock_connect: int = 10


@dataclass
class SSEConfig:
    """Configuration for Server-Sent Events (SSE) streaming.

    Attributes:
        reconnect_interval: Seconds between reconnection attempts (default: 5)
        max_reconnect_attempts: Maximum reconnection attempts (default: 10)
        heartbeat_interval: Seconds between heartbeat checks (default: 30)
        buffer_size: Size of the event buffer (default: 100)
    """

    reconnect_interval: int = DEFAULT_RECONNECT_INTERVAL
    max_reconnect_attempts: int = DEFAULT_RECONNECT_ATTEMPTS
    heartbeat_interval: int = 30
    buffer_size: int = 100


@dataclass
class LoggingConfig:
    """Configuration for SDK logging.

    Attributes:
        enabled: Whether logging is enabled (default: True)
        level: Logging level (default: "INFO")
        log_requests: Whether to log HTTP requests (default: False)
        log_responses: Whether to log HTTP responses (default: False)
        redact_sensitive: Whether to redact sensitive data (default: True)
    """

    enabled: bool = True
    level: str = "INFO"
    log_requests: bool = False
    log_responses: bool = False
    redact_sensitive: bool = True


@dataclass
class SnapPayConfig:
    """Main configuration class for SnapPay SDK.

    This class centralizes all SDK configuration options including
    API settings, retry policies, timeouts, and logging preferences.

    Attributes:
        api_key: SnapPay API key (required)
        base_url: Base URL for API endpoints
        user_agent: User agent string for requests
        retry: Retry configuration
        timeout: Timeout configuration
        sse: SSE streaming configuration
        logging: Logging configuration
        custom_headers: Additional headers to include in requests
        verify_ssl: Whether to verify SSL certificates
        proxy: Proxy configuration (if needed)

    Example:
        >>> from snappay import SnapPay, SnapPayConfig, RetryConfig
        >>>
        >>> config = SnapPayConfig(
        ...     api_key="pk_test_abc123",
        ...     retry=RetryConfig(max_retries=5),
        ...     logging=LoggingConfig(log_requests=True)
        ... )
        >>> client = SnapPay(config=config)
    """

    api_key: Optional[str] = field(default=None)
    base_url: str = field(default=DEFAULT_BASE_URL)
    user_agent: str = field(default=f"snappay-python/{SDK_VERSION}")
    retry: RetryConfig = field(default_factory=RetryConfig)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    sse: SSEConfig = field(default_factory=SSEConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = field(default=True)
    proxy: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        # Try to get API key from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("SNAPPAY_API_KEY")

        # Normalize base URL
        self.base_url = self.base_url.rstrip("/")

        # Validate API key format if provided
        if self.api_key:
            self._validate_api_key()

    def _validate_api_key(self) -> None:
        """Validate the API key format."""
        if not self.api_key:
            return

        if not isinstance(self.api_key, str):
            raise AuthenticationError("API key must be a string")

        if not self.api_key.strip():
            raise AuthenticationError("API key must be provided")

        # Check for valid prefixes
        valid_prefixes = ("pk_test_", "pk_live_")
        if not any(self.api_key.startswith(prefix) for prefix in valid_prefixes):
            raise AuthenticationError(
                f"Invalid API key format. Must start with one of: {', '.join(valid_prefixes)}"
            )

    @classmethod
    def from_env(cls, **overrides: Any) -> "SnapPayConfig":
        """Create configuration from environment variables.

        Environment variables:
            SNAPPAY_API_KEY: API key
            SNAPPAY_BASE_URL: Base URL
            SNAPPAY_MAX_RETRIES: Maximum retry attempts
            SNAPPAY_TIMEOUT: Request timeout
            SNAPPAY_LOG_LEVEL: Logging level
            SNAPPAY_VERIFY_SSL: Whether to verify SSL

        Args:
            **overrides: Additional configuration overrides

        Returns:
            SnapPayConfig instance
        """
        config_dict: Dict[str, Any] = {}

        # Map environment variables to configuration
        env_mapping = {
            "SNAPPAY_API_KEY": "api_key",
            "SNAPPAY_BASE_URL": "base_url",
            "SNAPPAY_USER_AGENT": "user_agent",
            "SNAPPAY_VERIFY_SSL": "verify_ssl",
            "SNAPPAY_PROXY": "proxy",
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert boolean strings
                if config_key == "verify_ssl":
                    config_dict[config_key] = value.lower() in ("true", "1", "yes")
                else:
                    config_dict[config_key] = value

        # Handle nested configurations
        max_retries_env = os.getenv("SNAPPAY_MAX_RETRIES")
        if max_retries_env:
            if "retry" not in config_dict:
                config_dict["retry"] = RetryConfig()
            config_dict["retry"].max_retries = int(max_retries_env)

        timeout_env = os.getenv("SNAPPAY_TIMEOUT")
        if timeout_env:
            if "timeout" not in config_dict:
                config_dict["timeout"] = TimeoutConfig()
            config_dict["timeout"].total = int(timeout_env)

        log_level_env = os.getenv("SNAPPAY_LOG_LEVEL")
        if log_level_env:
            if "logging" not in config_dict:
                config_dict["logging"] = LoggingConfig()
            config_dict["logging"].level = log_level_env

        # Apply overrides
        config_dict.update(overrides)

        return cls(**config_dict)

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "api_key": "***" if self.api_key else None,  # Redact API key
            "base_url": self.base_url,
            "user_agent": self.user_agent,
            "retry": {
                "max_retries": self.retry.max_retries,
                "base_delay": self.retry.base_delay,
                "max_delay": self.retry.max_delay,
            },
            "timeout": {
                "total": self.timeout.total,
                "connect": self.timeout.connect,
            },
            "sse": {
                "reconnect_interval": self.sse.reconnect_interval,
                "max_reconnect_attempts": self.sse.max_reconnect_attempts,
            },
            "logging": {
                "enabled": self.logging.enabled,
                "level": self.logging.level,
            },
            "verify_ssl": self.verify_ssl,
        }
