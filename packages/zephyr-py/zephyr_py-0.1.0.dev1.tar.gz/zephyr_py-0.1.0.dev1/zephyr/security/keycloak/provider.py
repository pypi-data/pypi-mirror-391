"""
Keycloak SSO provider integration.

Integrates Keycloak with the Zephyr SSO system.
"""

from typing import Any

from ..sso.models import SSOAuthResult, SSOUser
from ..sso.providers import SSOProvider
from .client import KeycloakClient
from .config import KeycloakConfig
from .exceptions import KeycloakError


class KeycloakSSOProvider(SSOProvider):
    """Keycloak SSO provider."""

    def __init__(self, config: KeycloakConfig) -> None:
        """
        Initialize Keycloak SSO provider.

        Args:
            config: Keycloak configuration
        """
        super().__init__(config.dict())
        self.keycloak_config = config
        self.keycloak_client = KeycloakClient(config)

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "keycloak"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """
        Get OAuth authorization URL.

        Args:
            state: State parameter for CSRF protection
            **kwargs: Additional parameters

        Returns:
            Authorization URL
        """
        redirect_uri = kwargs.pop("redirect_uri", None)
        if not redirect_uri:
            raise ValueError("redirect_uri is required")

        scopes = kwargs.pop("scopes", None)
        return self.keycloak_client.get_authorization_url(
            redirect_uri=redirect_uri, state=state, scopes=scopes, **kwargs
        )

    async def exchange_code_for_token(self, code: str, state: str) -> dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code
            state: State parameter

        Returns:
            Token data

        Raises:
            SSOAuthError: If token exchange fails
        """
        from ..sso.exceptions import SSOAuthError

        try:
            # Note: redirect_uri should be passed via kwargs in real implementation
            # For now, we'll need to get it from somewhere
            redirect_uri = self.config.get("redirect_uri", "")
            code_verifier = self.config.get("code_verifier")

            token = await self.keycloak_client.exchange_code_for_token(
                code=code, redirect_uri=redirect_uri, code_verifier=code_verifier
            )

            return token.dict()

        except KeycloakError as e:
            raise SSOAuthError(str(e), provider=self.provider_name)

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from provider.

        Args:
            access_token: Access token

        Returns:
            User information

        Raises:
            SSOAuthError: If request fails
        """
        from ..sso.exceptions import SSOAuthError

        try:
            user_info = await self.keycloak_client.get_user_info(access_token)
            return user_info.dict()

        except KeycloakError as e:
            raise SSOAuthError(str(e), provider=self.provider_name)

    def map_user_data(self, user_data: dict[str, Any]) -> SSOUser:
        """
        Map provider user data to SSOUser.

        Args:
            user_data: User data from Keycloak

        Returns:
            Mapped SSO user
        """
        mapping = self.keycloak_config.user_mapping

        return SSOUser(
            id=user_data.get(mapping.get("id", "sub"), ""),
            provider=self.provider_name,
            provider_user_id=user_data.get("sub", ""),
            email=user_data.get(mapping.get("email", "email"), ""),
            username=user_data.get(mapping.get("username", "preferred_username")),
            first_name=user_data.get(mapping.get("first_name", "given_name")),
            last_name=user_data.get(mapping.get("last_name", "family_name")),
            display_name=user_data.get(mapping.get("display_name", "name")),
            avatar_url=user_data.get(mapping.get("avatar_url", "picture")),
            locale=user_data.get(mapping.get("locale", "locale")),
            timezone=user_data.get(mapping.get("timezone", "zoneinfo")),
            is_verified=user_data.get(mapping.get("is_verified", "email_verified"), False),
            provider_data=user_data,
        )

    async def authenticate(self, code: str, state: str) -> SSOAuthResult:
        """
        Complete authentication flow.

        Args:
            code: Authorization code
            state: State parameter

        Returns:
            Authentication result
        """
        try:
            # Exchange code for token
            token_data = await self.exchange_code_for_token(code, state)

            # Get user info
            user_data = await self.get_user_info(token_data["access_token"])

            # Map user data
            user = self.map_user_data(user_data)

            return SSOAuthResult.success_result(
                user=user, provider=self.provider_name, state=state, metadata={"token_data": token_data}
            )

        except Exception as e:
            return SSOAuthResult.error_result(provider=self.provider_name, error=str(e), state=state)

    async def logout(self, refresh_token: str, redirect_uri: str | None = None) -> None:
        """
        Logout user from Keycloak.

        Args:
            refresh_token: Refresh token to invalidate
            redirect_uri: Optional redirect URI after logout

        Raises:
            SSOAuthError: If logout fails
        """
        from ..sso.exceptions import SSOAuthError

        try:
            await self.keycloak_client.logout(refresh_token=refresh_token, redirect_uri=redirect_uri)

        except KeycloakError as e:
            raise SSOAuthError(str(e), provider=self.provider_name)

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            New token data

        Raises:
            SSOAuthError: If refresh fails
        """
        from ..sso.exceptions import SSOAuthError

        try:
            token = await self.keycloak_client.refresh_token(refresh_token)
            return token.dict()

        except KeycloakError as e:
            raise SSOAuthError(str(e), provider=self.provider_name)

    async def validate_token(self, access_token: str) -> dict[str, Any]:
        """
        Validate access token.

        Args:
            access_token: Access token to validate

        Returns:
            Token claims

        Raises:
            SSOAuthError: If validation fails
        """
        from ..sso.exceptions import SSOAuthError

        try:
            claims = await self.keycloak_client.validate_token(access_token)
            return claims

        except KeycloakError as e:
            raise SSOAuthError(str(e), provider=self.provider_name)

    async def close(self) -> None:
        """Close HTTP client."""
        await self.keycloak_client.close()
