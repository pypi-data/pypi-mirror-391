"""
SSO exceptions and error handling.

Defines all SSO-specific exceptions with proper error codes and descriptions.
"""

from typing import Any, Dict, Optional


class SSOError(Exception):
    """Base SSO error class."""

    def __init__(self, message: str, error_code: str | None = None, provider: str | None = None, **kwargs: Any) -> None:
        """
        Initialize SSO error.

        Args:
            message: Error message
            error_code: Error code
            provider: SSO provider name
            **kwargs: Additional error parameters
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.provider = provider
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        result = {"error": "sso_error", "message": self.message}

        if self.error_code:
            result["error_code"] = self.error_code
        if self.provider:
            result["provider"] = self.provider

        result.update(self.extra)
        return result


class SSOProviderError(SSOError):
    """SSO provider error."""

    def __init__(self, message: str, provider: str, error_code: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code=error_code or "provider_error", provider=provider, **kwargs)


class SSOAuthError(SSOError):
    """SSO authentication error."""

    def __init__(self, message: str, provider: str, error_code: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code=error_code or "auth_error", provider=provider, **kwargs)


class SSOConfigError(SSOError):
    """SSO configuration error."""

    def __init__(self, message: str, provider: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="config_error", provider=provider, **kwargs)


class SSOUserNotFoundError(SSOError):
    """SSO user not found error."""

    def __init__(
        self, message: str = "User not found", provider: str | None = None, user_id: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message=message, error_code="user_not_found", provider=provider, user_id=user_id, **kwargs)


class SSOProviderNotFoundError(SSOError):
    """SSO provider not found error."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"SSO provider '{provider}' not found", error_code="provider_not_found", provider=provider, **kwargs
        )


class SSOInvalidStateError(SSOError):
    """SSO invalid state error."""

    def __init__(
        self, message: str = "Invalid or expired state parameter", state: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message=message, error_code="invalid_state", state=state, **kwargs)


class SSOAuthCancelledError(SSOError):
    """SSO authentication cancelled error."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        super().__init__(
            message="Authentication was cancelled by user", error_code="auth_cancelled", provider=provider, **kwargs
        )


class SSOAuthTimeoutError(SSOError):
    """SSO authentication timeout error."""

    def __init__(self, provider: str, timeout_seconds: int | None = None, **kwargs: Any) -> None:
        message = "Authentication timed out"
        if timeout_seconds:
            message += f" after {timeout_seconds} seconds"

        super().__init__(
            message=message, error_code="auth_timeout", provider=provider, timeout_seconds=timeout_seconds, **kwargs
        )


class SSOInvalidCredentialsError(SSOError):
    """SSO invalid credentials error."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        super().__init__(
            message="Invalid credentials provided", error_code="invalid_credentials", provider=provider, **kwargs
        )


class SSOAccessDeniedError(SSOError):
    """SSO access denied error."""

    def __init__(self, provider: str, reason: str | None = None, **kwargs: Any) -> None:
        message = "Access denied"
        if reason:
            message += f": {reason}"

        super().__init__(message=message, error_code="access_denied", provider=provider, reason=reason, **kwargs)


class SSOProviderUnavailableError(SSOError):
    """SSO provider unavailable error."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"SSO provider '{provider}' is currently unavailable",
            error_code="provider_unavailable",
            provider=provider,
            **kwargs,
        )


class SSOInvalidResponseError(SSOError):
    """SSO invalid response error."""

    def __init__(self, provider: str, response_data: Any | None = None, **kwargs: Any) -> None:
        super().__init__(
            message="Invalid response from SSO provider",
            error_code="invalid_response",
            provider=provider,
            response_data=response_data,
            **kwargs,
        )


class SSOTokenExpiredError(SSOError):
    """SSO token expired error."""

    def __init__(self, provider: str, token_type: str | None = None, **kwargs: Any) -> None:
        message = "Token has expired"
        if token_type:
            message += f" ({token_type})"

        super().__init__(
            message=message, error_code="token_expired", provider=provider, token_type=token_type, **kwargs
        )


class SSOInvalidTokenError(SSOError):
    """SSO invalid token error."""

    def __init__(self, provider: str, token_type: str | None = None, **kwargs: Any) -> None:
        message = "Invalid token"
        if token_type:
            message += f" ({token_type})"

        super().__init__(
            message=message, error_code="invalid_token", provider=provider, token_type=token_type, **kwargs
        )


class SSORateLimitError(SSOError):
    """SSO rate limit error."""

    def __init__(self, provider: str, retry_after: int | None = None, **kwargs: Any) -> None:
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"

        super().__init__(message=message, error_code="rate_limit", provider=provider, retry_after=retry_after, **kwargs)


class SSONetworkError(SSOError):
    """SSO network error."""

    def __init__(self, provider: str, original_error: Exception | None = None, **kwargs: Any) -> None:
        message = "Network error occurred"
        if original_error:
            message += f": {str(original_error)}"

        super().__init__(
            message=message,
            error_code="network_error",
            provider=provider,
            original_error=str(original_error) if original_error else None,
            **kwargs,
        )


class SSOValidationError(SSOError):
    """SSO validation error."""

    def __init__(self, message: str, field: str | None = None, value: Any | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="validation_error", field=field, value=value, **kwargs)


class SSOUnsupportedProviderError(SSOError):
    """SSO unsupported provider error."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"SSO provider '{provider}' is not supported",
            error_code="unsupported_provider",
            provider=provider,
            **kwargs,
        )


class SSOProviderConfigurationError(SSOError):
    """SSO provider configuration error."""

    def __init__(self, provider: str, config_field: str | None = None, **kwargs: Any) -> None:
        message = f"Invalid configuration for provider '{provider}'"
        if config_field:
            message += f" (field: {config_field})"

        super().__init__(
            message=message, error_code="provider_config_error", provider=provider, config_field=config_field, **kwargs
        )


class SSOUserMappingError(SSOError):
    """SSO user mapping error."""

    def __init__(self, provider: str, sso_user_data: Dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(
            message="Failed to map SSO user data to application user",
            error_code="user_mapping_error",
            provider=provider,
            sso_user_data=sso_user_data,
            **kwargs,
        )


class SSOAttributeMappingError(SSOError):
    """SSO attribute mapping error."""

    def __init__(self, provider: str, attribute: str | None = None, **kwargs: Any) -> None:
        message = "Failed to map SSO attribute"
        if attribute:
            message += f" '{attribute}'"

        super().__init__(
            message=message, error_code="attribute_mapping_error", provider=provider, attribute=attribute, **kwargs
        )
