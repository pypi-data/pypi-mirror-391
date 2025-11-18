"""
OAuth2 Server Implementation for Zephyr.

Provides comprehensive OAuth2 authorization server functionality including
Authorization Code, Client Credentials, PKCE, and Device flows.
"""

from .server import OAuth2Server, OAuth2Config
from .flows import AuthorizationCodeFlow, ClientCredentialsFlow, PKCEFlow, DeviceFlow, RefreshTokenFlow
from .models import (
    OAuth2Client,
    OAuth2AuthorizationCode,
    OAuth2AccessToken,
    OAuth2RefreshToken,
    OAuth2Scope,
    OAuth2Grant,
)
from .exceptions import (
    OAuth2Error,
    InvalidClientError,
    InvalidGrantError,
    InvalidRequestError,
    InvalidScopeError,
    UnsupportedGrantTypeError,
    UnsupportedResponseTypeError,
    AccessDeniedError,
    ServerError,
)
from .endpoints import AuthorizationEndpoint, TokenEndpoint, RevocationEndpoint, IntrospectionEndpoint

__all__ = [
    # Server
    "OAuth2Server",
    "OAuth2Config",
    # Flows
    "AuthorizationCodeFlow",
    "ClientCredentialsFlow",
    "PKCEFlow",
    "DeviceFlow",
    "RefreshTokenFlow",
    # Models
    "OAuth2Client",
    "OAuth2AuthorizationCode",
    "OAuth2AccessToken",
    "OAuth2RefreshToken",
    "OAuth2Scope",
    "OAuth2Grant",
    # Exceptions
    "OAuth2Error",
    "InvalidClientError",
    "InvalidGrantError",
    "InvalidRequestError",
    "InvalidScopeError",
    "UnsupportedGrantTypeError",
    "UnsupportedResponseTypeError",
    "AccessDeniedError",
    "ServerError",
    # Endpoints
    "AuthorizationEndpoint",
    "TokenEndpoint",
    "RevocationEndpoint",
    "IntrospectionEndpoint",
]
