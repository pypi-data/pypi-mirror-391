"""
SSO manager for handling multiple SSO providers.

Provides centralized management of SSO providers, authentication flows, and user sessions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .config import SSOConfig
from .exceptions import (
    SSOConfigError,
    SSOProviderNotFoundError,
    SSOUnsupportedProviderError,
)
from .models import SSOAuthResult, SSOAuthState, SSOUser, create_auth_state
from .providers import SSOProvider, create_sso_provider


class SSOManager:
    """
    SSO manager for handling multiple SSO providers.

    Provides centralized management of SSO providers, authentication flows,
    and user sessions with support for multiple identity providers.
    """

    def __init__(self, config: SSOConfig) -> None:
        """
        Initialize SSO manager.

        Args:
            config: SSO configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, SSOProvider] = {}
        self.auth_states: Dict[str, SSOAuthState] = {}

        # Initialize providers
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize SSO providers from configuration."""
        for provider_name in self.config.enabled_providers:
            try:
                provider_config = self.config.get_provider_config(provider_name)
                if not provider_config:
                    self.logger.warning(f"No configuration found for provider: {provider_name}")
                    continue

                provider = create_sso_provider(provider_name, provider_config)
                self.providers[provider_name] = provider

                self.logger.info(f"Initialized SSO provider: {provider_name}")

            except Exception as e:
                self.logger.error(f"Failed to initialize provider {provider_name}: {e}")

    def get_provider(self, provider_name: str) -> SSOProvider:
        """
        Get SSO provider by name.

        Args:
            provider_name: Provider name

        Returns:
            SSO provider instance

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        provider_name = provider_name.lower()

        if provider_name not in self.providers:
            raise SSOProviderNotFoundError(provider_name)

        return self.providers[provider_name]

    def get_available_providers(self) -> List[str]:
        """
        Get list of available SSO providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def is_provider_available(self, provider_name: str) -> bool:
        """
        Check if provider is available.

        Args:
            provider_name: Provider name

        Returns:
            True if provider is available, False otherwise
        """
        return provider_name.lower() in self.providers

    def create_auth_state(
        self, provider: str, redirect_url: Optional[str] = None, user_id: Optional[str] = None, **kwargs: Any
    ) -> SSOAuthState:
        """
        Create authentication state.

        Args:
            provider: SSO provider name
            redirect_url: Redirect URL after authentication
            user_id: User ID if already authenticated
            **kwargs: Additional state metadata

        Returns:
            Authentication state

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        if not self.is_provider_available(provider):
            raise SSOProviderNotFoundError(provider)

        state = create_auth_state(
            provider=provider,
            expires_in=self.config.state_lifetime,
            redirect_url=redirect_url,
            user_id=user_id,
            **kwargs,
        )

        self.auth_states[state.state] = state

        return state

    def get_auth_state(self, state: str) -> Optional[SSOAuthState]:
        """
        Get authentication state by state parameter.

        Args:
            state: State parameter

        Returns:
            Authentication state if found and valid, None otherwise
        """
        auth_state = self.auth_states.get(state)

        if not auth_state:
            return None

        if not auth_state.is_valid():
            # Clean up expired state
            del self.auth_states[state]
            return None

        return auth_state

    def mark_auth_state_used(self, state: str) -> None:
        """
        Mark authentication state as used.

        Args:
            state: State parameter
        """
        auth_state = self.auth_states.get(state)
        if auth_state:
            auth_state.mark_as_used()

    def get_authorization_url(
        self, provider: str, redirect_url: Optional[str] = None, user_id: Optional[str] = None, **kwargs: Any
    ) -> str:
        """
        Get OAuth authorization URL for provider.

        Args:
            provider: SSO provider name
            redirect_url: Redirect URL after authentication
            user_id: User ID if already authenticated
            **kwargs: Additional parameters

        Returns:
            Authorization URL

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        sso_provider = self.get_provider(provider)

        # Create authentication state
        auth_state = self.create_auth_state(provider=provider, redirect_url=redirect_url, user_id=user_id, **kwargs)

        # Get authorization URL
        return sso_provider.get_authorization_url(auth_state.state, **kwargs)

    async def authenticate(self, provider: str, code: str, state: str) -> SSOAuthResult:
        """
        Complete authentication flow.

        Args:
            provider: SSO provider name
            code: Authorization code
            state: Authentication state

        Returns:
            Authentication result

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        # Validate authentication state
        auth_state = self.get_auth_state(state)
        if not auth_state:
            return SSOAuthResult.error_result(
                provider=provider, error="Invalid or expired state parameter", error_code="invalid_state", state=state
            )

        if auth_state.provider != provider:
            return SSOAuthResult.error_result(
                provider=provider, error="Provider mismatch", error_code="provider_mismatch", state=state
            )

        # Get provider
        sso_provider = self.get_provider(provider)

        try:
            # Complete authentication
            result = await sso_provider.authenticate(code, state)

            # Mark state as used
            self.mark_auth_state_used(state)

            # Set redirect URL from state
            if result.success and auth_state.redirect_url:
                result.redirect_url = auth_state.redirect_url

            return result

        except Exception as e:
            self.logger.error(f"Authentication failed for provider {provider}: {e}")
            return SSOAuthResult.error_result(provider=provider, error=str(e), state=state)

    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information from provider.

        Args:
            provider: SSO provider name
            access_token: Access token

        Returns:
            User information

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        sso_provider = self.get_provider(provider)
        return await sso_provider.get_user_info(access_token)

    def map_user_data(self, provider: str, user_data: Dict[str, Any]) -> SSOUser:
        """
        Map provider user data to SSOUser.

        Args:
            provider: SSO provider name
            user_data: Provider user data

        Returns:
            Mapped SSO user

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        sso_provider = self.get_provider(provider)
        return sso_provider.map_user_data(user_data)

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """
        Get provider information.

        Args:
            provider: Provider name

        Returns:
            Provider information

        Raises:
            SSOProviderNotFoundError: If provider is not found
        """
        if not self.is_provider_available(provider):
            raise SSOProviderNotFoundError(provider)

        provider_config = self.config.get_provider_config(provider)

        return {
            "name": provider,
            "display_name": provider.replace("_", " ").title(),
            "is_enabled": True,
            "is_configured": provider_config is not None,
            "scopes": provider_config.get("scopes", []) if provider_config else [],
            "metadata": provider_config.get("metadata", {}) if provider_config else {},
        }

    def get_all_providers_info(self) -> List[Dict[str, Any]]:
        """
        Get information for all providers.

        Returns:
            List of provider information
        """
        providers_info = []

        for provider_name in self.config.enabled_providers:
            try:
                info = self.get_provider_info(provider_name)
                providers_info.append(info)
            except Exception as e:
                self.logger.error(f"Failed to get info for provider {provider_name}: {e}")

        return providers_info

    def cleanup_expired_states(self) -> int:
        """
        Clean up expired authentication states.

        Returns:
            Number of states cleaned up
        """
        expired_states = []

        for state, auth_state in self.auth_states.items():
            if not auth_state.is_valid():
                expired_states.append(state)

        for state in expired_states:
            del self.auth_states[state]

        return len(expired_states)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get SSO manager statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "total_providers": len(self.providers),
            "enabled_providers": self.config.enabled_providers,
            "active_states": len(self.auth_states),
            "expired_states": self.cleanup_expired_states(),
            "config": {
                "enabled": self.config.enabled,
                "auto_register": self.config.auto_register,
                "auto_activate": self.config.auto_activate,
                "require_email_verification": self.config.require_email_verification,
            },
        }

    async def close(self) -> None:
        """Close all providers and clean up resources."""
        for provider in self.providers.values():
            try:
                await provider.close()
            except Exception as e:
                self.logger.error(f"Error closing provider: {e}")

        self.providers.clear()
        self.auth_states.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Note: This is synchronous, but close() is async
        # In a real implementation, you'd want to handle this properly
        pass
