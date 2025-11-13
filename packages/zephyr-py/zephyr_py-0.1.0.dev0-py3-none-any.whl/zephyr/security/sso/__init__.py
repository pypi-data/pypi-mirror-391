"""
Single Sign-On (SSO) providers for Zephyr.

Provides comprehensive SSO integration with major identity providers including
Google, GitHub, Microsoft, Apple, and SAML.
"""

from .providers import (
    SSOProvider,
    GoogleSSOProvider,
    GitHubSSOProvider,
    MicrosoftSSOProvider,
    AppleSSOProvider,
    SAMLSSOProvider,
    GenericOAuth2SSOProvider,
)
from .config import SSOConfig
from .models import SSOUser, SSOProviderInfo, SSOProviderConfig, SSOAuthState, SSOAuthResult
from .exceptions import (
    SSOError,
    SSOProviderError,
    SSOAuthError,
    SSOConfigError,
    SSOUserNotFoundError,
    SSOProviderNotFoundError,
    SSOInvalidStateError,
    SSOAuthCancelledError,
    SSOAuthTimeoutError,
)
from .manager import SSOManager

__all__ = [
    # Providers
    "SSOProvider",
    "GoogleSSOProvider",
    "GitHubSSOProvider",
    "MicrosoftSSOProvider",
    "AppleSSOProvider",
    "SAMLSSOProvider",
    "GenericOAuth2SSOProvider",
    # Configuration
    "SSOConfig",
    # Models
    "SSOUser",
    "SSOProviderInfo",
    "SSOProviderConfig",
    "SSOAuthState",
    "SSOAuthResult",
    # Exceptions
    "SSOError",
    "SSOProviderError",
    "SSOAuthError",
    "SSOConfigError",
    "SSOUserNotFoundError",
    "SSOProviderNotFoundError",
    "SSOInvalidStateError",
    "SSOAuthCancelledError",
    "SSOAuthTimeoutError",
    # Manager
    "SSOManager",
]
