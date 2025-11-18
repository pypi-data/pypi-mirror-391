"""
OAuth2 exceptions and error handling.

Defines all OAuth2-specific exceptions with proper error codes and descriptions.
"""

from typing import Any, Dict, Optional


class OAuth2Error(Exception):
    """Base OAuth2 error class."""

    def __init__(
        self,
        error: str,
        description: str | None = None,
        uri: str | None = None,
        state: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize OAuth2 error.

        Args:
            error: Error code
            description: Human-readable error description
            uri: URI identifying the error
            state: State parameter from request
            **kwargs: Additional error parameters
        """
        super().__init__(description or error)
        self.error = error
        self.description = description
        self.uri = uri
        self.state = state
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        result = {"error": self.error}

        if self.description:
            result["error_description"] = self.description
        if self.uri:
            result["error_uri"] = self.uri
        if self.state:
            result["state"] = self.state

        result.update(self.extra)
        return result


class InvalidRequestError(OAuth2Error):
    """Invalid request error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request",
            description=description
            or "The request is missing a required parameter, includes an invalid parameter value, includes a parameter more than once, or is otherwise malformed.",
            **kwargs,
        )


class InvalidClientError(OAuth2Error):
    """Invalid client error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_client",
            description=description
            or "Client authentication failed due to unknown client, no client authentication included, or unsupported authentication method.",
            **kwargs,
        )


class InvalidGrantError(OAuth2Error):
    """Invalid grant error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_grant",
            description=description
            or "The provided authorization grant is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client.",
            **kwargs,
        )


class UnauthorizedClientError(OAuth2Error):
    """Unauthorized client error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unauthorized_client",
            description=description
            or "The client is not authorized to request an authorization code using this method.",
            **kwargs,
        )


class UnsupportedGrantTypeError(OAuth2Error):
    """Unsupported grant type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unsupported_grant_type",
            description=description or "The authorization grant type is not supported by the authorization server.",
            **kwargs,
        )


class UnsupportedResponseTypeError(OAuth2Error):
    """Unsupported response type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unsupported_response_type",
            description=description
            or "The authorization server does not support obtaining an authorization code using this method.",
            **kwargs,
        )


class InvalidScopeError(OAuth2Error):
    """Invalid scope error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_scope",
            description=description or "The requested scope is invalid, unknown, or malformed.",
            **kwargs,
        )


class AccessDeniedError(OAuth2Error):
    """Access denied error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="access_denied",
            description=description or "The resource owner or authorization server denied the request.",
            **kwargs,
        )


class UnsupportedTokenTypeError(OAuth2Error):
    """Unsupported token type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unsupported_token_type",
            description=description
            or "The authorization server does not support the revocation of the presented token type.",
            **kwargs,
        )


class ServerError(OAuth2Error):
    """Server error (500)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="server_error",
            description=description
            or "The authorization server encountered an unexpected condition that prevented it from fulfilling the request.",
            **kwargs,
        )


class TemporarilyUnavailableError(OAuth2Error):
    """Temporarily unavailable error (503)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="temporarily_unavailable",
            description=description
            or "The authorization server is currently unable to handle the request due to a temporary overloading or maintenance of the server.",
            **kwargs,
        )


class InsufficientScopeError(OAuth2Error):
    """Insufficient scope error (403)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="insufficient_scope",
            description=description or "The request requires higher privileges than provided by the access token.",
            **kwargs,
        )


class InvalidTokenError(OAuth2Error):
    """Invalid token error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_token",
            description=description
            or "The access token provided is expired, revoked, malformed, or invalid for other reasons.",
            **kwargs,
        )


class ExpiredTokenError(OAuth2Error):
    """Expired token error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_token", description=description or "The access token provided has expired.", **kwargs
        )


class RevokedTokenError(OAuth2Error):
    """Revoked token error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_token", description=description or "The access token provided has been revoked.", **kwargs
        )


class MalformedTokenError(OAuth2Error):
    """Malformed token error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_token", description=description or "The access token provided is malformed.", **kwargs
        )


class MissingTokenError(OAuth2Error):
    """Missing token error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request",
            description=description or "The request is missing a required access token.",
            **kwargs,
        )


class InvalidRedirectUriError(OAuth2Error):
    """Invalid redirect URI error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request",
            description=description
            or "The redirect URI provided does not match a pre-registered redirect URI for this client.",
            **kwargs,
        )


class InvalidCodeChallengeError(OAuth2Error):
    """Invalid code challenge error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request",
            description=description or "The code challenge provided is invalid or malformed.",
            **kwargs,
        )


class InvalidCodeVerifierError(OAuth2Error):
    """Invalid code verifier error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_grant",
            description=description or "The code verifier provided does not match the code challenge.",
            **kwargs,
        )


class InvalidClientCredentialsError(OAuth2Error):
    """Invalid client credentials error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_client", description=description or "The client credentials provided are invalid.", **kwargs
        )


class ClientNotFoundError(OAuth2Error):
    """Client not found error (401)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_client",
            description=description or "The client specified in the request was not found.",
            **kwargs,
        )


class DuplicateClientError(OAuth2Error):
    """Duplicate client error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request",
            description=description or "A client with the specified identifier already exists.",
            **kwargs,
        )


class InvalidClientTypeError(OAuth2Error):
    """Invalid client type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_request", description=description or "The client type specified is not supported.", **kwargs
        )


class InvalidGrantTypeError(OAuth2Error):
    """Invalid grant type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unsupported_grant_type",
            description=description or "The grant type specified is not supported by this client.",
            **kwargs,
        )


class InvalidResponseTypeError(OAuth2Error):
    """Invalid response type error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="unsupported_response_type",
            description=description or "The response type specified is not supported by this client.",
            **kwargs,
        )


class InvalidScopeRequestError(OAuth2Error):
    """Invalid scope request error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_scope",
            description=description or "The scope requested is not valid for this client.",
            **kwargs,
        )


class AuthorizationExpiredError(OAuth2Error):
    """Authorization expired error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_grant", description=description or "The authorization code has expired.", **kwargs
        )


class AuthorizationUsedError(OAuth2Error):
    """Authorization used error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_grant", description=description or "The authorization code has already been used.", **kwargs
        )


class AuthorizationRevokedError(OAuth2Error):
    """Authorization revoked error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="invalid_grant", description=description or "The authorization code has been revoked.", **kwargs
        )


class DeviceCodeExpiredError(OAuth2Error):
    """Device code expired error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(error="expired_token", description=description or "The device code has expired.", **kwargs)


class DeviceCodePendingError(OAuth2Error):
    """Device code pending error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="authorization_pending",
            description=description
            or "The authorization request is still pending as the end user hasn't yet completed the user-interaction steps.",
            **kwargs,
        )


class DeviceCodeSlowDownError(OAuth2Error):
    """Device code slow down error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="slow_down", description=description or "The client is polling too frequently.", **kwargs
        )


class DeviceCodeAccessDeniedError(OAuth2Error):
    """Device code access denied error (400)."""

    def __init__(self, description: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            error="access_denied", description=description or "The end user denied the authorization request.", **kwargs
        )
