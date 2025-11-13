"""
Keycloak integration for Zephyr applications.

Provides Keycloak OAuth2/OIDC authentication, Admin API client, and SSO integration.
"""

from .admin import KeycloakAdmin
from .client import KeycloakClient
from .config import KeycloakConfig, KeycloakRealmConfig
from .exceptions import (
    KeycloakAdminError,
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakError,
    KeycloakExpiredTokenError,
    KeycloakInvalidTokenError,
    KeycloakRealmNotFoundError,
    KeycloakTokenError,
    KeycloakUserNotFoundError,
)
from .models import (
    KeycloakClient as KeycloakClientModel,
    KeycloakGroup,
    KeycloakRealm,
    KeycloakRole,
    KeycloakToken,
    KeycloakUser,
    KeycloakUserInfo,
)
from .provider import KeycloakSSOProvider

__all__ = [
    # Client
    "KeycloakClient",
    "KeycloakAdmin",
    # Configuration
    "KeycloakConfig",
    "KeycloakRealmConfig",
    # Models
    "KeycloakToken",
    "KeycloakUser",
    "KeycloakUserInfo",
    "KeycloakRole",
    "KeycloakGroup",
    "KeycloakClientModel",
    "KeycloakRealm",
    # Exceptions
    "KeycloakError",
    "KeycloakConnectionError",
    "KeycloakAuthenticationError",
    "KeycloakTokenError",
    "KeycloakAdminError",
    "KeycloakRealmNotFoundError",
    "KeycloakUserNotFoundError",
    "KeycloakInvalidTokenError",
    "KeycloakExpiredTokenError",
    # Provider
    "KeycloakSSOProvider",
]
