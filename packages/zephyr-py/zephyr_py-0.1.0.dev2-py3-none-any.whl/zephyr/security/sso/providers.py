"""
SSO provider implementations.

Implements SSO providers for Google, GitHub, Microsoft, Apple, SAML, and generic OAuth2.
"""

import hashlib
import hmac
import json
import secrets
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf import pbkdf2
from jose import jwt

from .config import (
    AppleSSOConfig,
    GenericOAuth2SSOConfig,
    GitHubSSOConfig,
    GoogleSSOConfig,
    MicrosoftSSOConfig,
    SAMLSSOConfig,
)
from .exceptions import (
    SSOAuthError,
    SSOConfigError,
    SSOInvalidResponseError,
    SSONetworkError,
    SSOProviderError,
    SSOUnsupportedProviderError,
)
from .models import SSOAuthResult, SSOAuthState, SSOUser, create_auth_state


class SSOProvider(ABC):
    """Base class for SSO providers."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize SSO provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.provider_name = self.get_provider_name()
        self.http_client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass

    @abstractmethod
    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get OAuth authorization URL."""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider."""
        pass

    @abstractmethod
    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map provider user data to SSOUser."""
        pass

    async def authenticate(self, code: str, state: str) -> SSOAuthResult:
        """
        Complete authentication flow.

        Args:
            code: Authorization code
            state: Authentication state

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

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()


class GoogleSSOProvider(SSOProvider):
    """Google SSO provider."""

    def __init__(self, config: GoogleSSOConfig) -> None:
        """Initialize Google SSO provider."""
        super().__init__(config.dict())
        self.google_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "google"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get Google OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.google_config.client_id,
            "redirect_uri": self.google_config.redirect_uri,
            "scope": " ".join(self.google_config.scopes),
            "state": state,
            "access_type": self.google_config.access_type,
            "prompt": self.google_config.prompt,
            "include_granted_scopes": str(self.google_config.include_granted_scopes).lower(),
        }

        if self.google_config.hosted_domain:
            params["hd"] = self.google_config.hosted_domain

        params.update(kwargs)

        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "code": code,
            "client_id": self.google_config.client_id,
            "client_secret": self.google_config.client_secret,
            "redirect_uri": self.google_config.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = await self.http_client.post(
            "https://oauth2.googleapis.com/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to exchange code for token: {response.text}", provider=self.provider_name)

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google."""
        response = await self.http_client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to get user info: {response.text}", provider=self.provider_name)

        return response.json()

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map Google user data to SSOUser."""
        mapping = self.google_config.user_mapping

        return SSOUser(
            id=user_data.get(mapping.get("id", "sub"), ""),
            provider=self.provider_name,
            provider_user_id=user_data.get("id", ""),
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


class GitHubSSOProvider(SSOProvider):
    """GitHub SSO provider."""

    def __init__(self, config: GitHubSSOConfig) -> None:
        """Initialize GitHub SSO provider."""
        super().__init__(config.dict())
        self.github_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "github"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get GitHub OAuth authorization URL."""
        params = {
            "client_id": self.github_config.client_id,
            "redirect_uri": self.github_config.redirect_uri,
            "scope": " ".join(self.github_config.scopes),
            "state": state,
            "allow_signup": str(self.github_config.allow_signup).lower(),
        }

        params.update(kwargs)

        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "client_id": self.github_config.client_id,
            "client_secret": self.github_config.client_secret,
            "code": code,
            "redirect_uri": self.github_config.redirect_uri,
        }

        response = await self.http_client.post(
            "https://github.com/login/oauth/access_token", data=data, headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to exchange code for token: {response.text}", provider=self.provider_name)

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub."""
        # Get user profile
        user_response = await self.http_client.get(
            "https://api.github.com/user", headers={"Authorization": f"token {access_token}"}
        )

        if user_response.status_code != 200:
            raise SSOAuthError(f"Failed to get user profile: {user_response.text}", provider=self.provider_name)

        user_data = user_response.json()

        # Get user emails
        emails_response = await self.http_client.get(
            "https://api.github.com/user/emails", headers={"Authorization": f"token {access_token}"}
        )

        if emails_response.status_code == 200:
            emails = emails_response.json()
            # Find primary email
            primary_email = next((email for email in emails if email.get("primary")), emails[0] if emails else None)
            if primary_email:
                user_data["email"] = primary_email["email"]
                user_data["email_verified"] = primary_email.get("verified", False)

        return user_data

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map GitHub user data to SSOUser."""
        mapping = self.github_config.user_mapping

        # Split name into first and last name
        name = user_data.get("name", "")
        first_name, last_name = "", ""
        if name:
            name_parts = name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        return SSOUser(
            id=user_data.get(mapping.get("id", "id"), ""),
            provider=self.provider_name,
            provider_user_id=str(user_data.get("id", "")),
            email=user_data.get(mapping.get("email", "email"), ""),
            username=user_data.get(mapping.get("username", "login")),
            first_name=first_name or user_data.get(mapping.get("first_name", "name")),
            last_name=last_name or user_data.get(mapping.get("last_name", "name")),
            display_name=user_data.get(mapping.get("display_name", "name")),
            avatar_url=user_data.get(mapping.get("avatar_url", "avatar_url")),
            locale=user_data.get(mapping.get("locale", "locale")),
            timezone=user_data.get(mapping.get("timezone", "timezone")),
            is_verified=user_data.get(mapping.get("is_verified", "email_verified"), False),
            provider_data=user_data,
        )


class MicrosoftSSOProvider(SSOProvider):
    """Microsoft SSO provider."""

    def __init__(self, config: MicrosoftSSOConfig) -> None:
        """Initialize Microsoft SSO provider."""
        super().__init__(config.dict())
        self.microsoft_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "microsoft"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get Microsoft OAuth authorization URL."""
        params = {
            "client_id": self.microsoft_config.client_id,
            "response_type": self.microsoft_config.response_type,
            "redirect_uri": self.microsoft_config.redirect_uri,
            "scope": " ".join(self.microsoft_config.scopes),
            "state": state,
            "response_mode": self.microsoft_config.response_mode,
        }

        params.update(kwargs)

        return f"https://login.microsoftonline.com/{self.microsoft_config.tenant}/oauth2/v2.0/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "client_id": self.microsoft_config.client_id,
            "client_secret": self.microsoft_config.client_secret,
            "code": code,
            "redirect_uri": self.microsoft_config.redirect_uri,
            "grant_type": "authorization_code",
            "scope": " ".join(self.microsoft_config.scopes),
        }

        response = await self.http_client.post(
            f"https://login.microsoftonline.com/{self.microsoft_config.tenant}/oauth2/v2.0/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to exchange code for token: {response.text}", provider=self.provider_name)

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft."""
        response = await self.http_client.get(
            "https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to get user info: {response.text}", provider=self.provider_name)

        return response.json()

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map Microsoft user data to SSOUser."""
        mapping = self.microsoft_config.user_mapping

        return SSOUser(
            id=user_data.get(mapping.get("id", "sub"), ""),
            provider=self.provider_name,
            provider_user_id=user_data.get("id", ""),
            email=user_data.get(mapping.get("email", "mail"), ""),
            username=user_data.get(mapping.get("username", "userPrincipalName")),
            first_name=user_data.get(mapping.get("first_name", "givenName")),
            last_name=user_data.get(mapping.get("last_name", "surname")),
            display_name=user_data.get(mapping.get("display_name", "displayName")),
            avatar_url=user_data.get(mapping.get("avatar_url", "picture")),
            locale=user_data.get(mapping.get("locale", "preferredLanguage")),
            timezone=user_data.get(mapping.get("timezone", "timezone")),
            is_verified=user_data.get(mapping.get("is_verified", "email_verified"), False),
            provider_data=user_data,
        )


class AppleSSOProvider(SSOProvider):
    """Apple SSO provider."""

    def __init__(self, config: AppleSSOConfig) -> None:
        """Initialize Apple SSO provider."""
        super().__init__(config.dict())
        self.apple_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "apple"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get Apple OAuth authorization URL."""
        params = {
            "response_type": "code",
            "response_mode": self.apple_config.response_mode,
            "client_id": self.apple_config.client_id,
            "redirect_uri": self.apple_config.redirect_uri,
            "scope": " ".join(self.apple_config.scopes),
            "state": state,
        }

        params.update(kwargs)

        return f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        # Generate client secret JWT
        client_secret = self._generate_client_secret()

        data = {
            "client_id": self.apple_config.client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": self.apple_config.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = await self.http_client.post(
            "https://appleid.apple.com/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to exchange code for token: {response.text}", provider=self.provider_name)

        return response.json()

    def _generate_client_secret(self) -> str:
        """Generate Apple client secret JWT."""
        now = int(time.time())

        payload = {
            "iss": self.apple_config.team_id,
            "iat": now,
            "exp": now + 3600,  # 1 hour
            "aud": "https://appleid.apple.com",
            "sub": self.apple_config.client_id,
        }

        # Load private key
        private_key = serialization.load_pem_private_key(self.apple_config.private_key.encode(), password=None)

        return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": self.apple_config.key_id})

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Apple."""
        # Apple doesn't provide user info endpoint
        # User info is only available in the ID token
        # This would typically decode the ID token to get user info
        return {}

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map Apple user data to SSOUser."""
        mapping = self.apple_config.user_mapping

        return SSOUser(
            id=user_data.get(mapping.get("id", "sub"), ""),
            provider=self.provider_name,
            provider_user_id=user_data.get("sub", ""),
            email=user_data.get(mapping.get("email", "email"), ""),
            username=user_data.get(mapping.get("username", "email")),
            first_name=user_data.get(mapping.get("first_name", "given_name")),
            last_name=user_data.get(mapping.get("last_name", "family_name")),
            display_name=user_data.get(mapping.get("display_name", "name")),
            is_verified=user_data.get(mapping.get("is_verified", "email_verified"), False),
            provider_data=user_data,
        )


class SAMLSSOProvider(SSOProvider):
    """SAML SSO provider."""

    def __init__(self, config: SAMLSSOConfig) -> None:
        """Initialize SAML SSO provider."""
        super().__init__(config.dict())
        self.saml_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "saml"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get SAML SSO URL."""
        # SAML doesn't use OAuth flow
        # This would typically generate a SAML request
        return self.saml_config.sso_url

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """SAML doesn't use OAuth flow."""
        raise SSOUnsupportedProviderError("SAML doesn't use OAuth flow")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """SAML doesn't use OAuth flow."""
        raise SSOUnsupportedProviderError("SAML doesn't use OAuth flow")

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map SAML user data to SSOUser."""
        mapping = self.saml_config.attribute_mapping

        return SSOUser(
            id=user_data.get(mapping.get("id", "sub"), ""),
            provider=self.provider_name,
            provider_user_id=user_data.get("sub", ""),
            email=user_data.get(mapping.get("email", "email"), ""),
            username=user_data.get(mapping.get("username", "name")),
            first_name=user_data.get(mapping.get("first_name", "given_name")),
            last_name=user_data.get(mapping.get("last_name", "surname")),
            display_name=user_data.get(mapping.get("display_name", "name")),
            is_verified=user_data.get(mapping.get("is_verified", "email_verified"), False),
            provider_data=user_data,
        )


class GenericOAuth2SSOProvider(SSOProvider):
    """Generic OAuth2 SSO provider."""

    def __init__(self, config: GenericOAuth2SSOConfig) -> None:
        """Initialize generic OAuth2 SSO provider."""
        super().__init__(config.dict())
        self.oauth2_config = config

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "generic_oauth2"

    def get_authorization_url(self, state: str, **kwargs: Any) -> str:
        """Get OAuth2 authorization URL."""
        params = {
            "response_type": self.oauth2_config.response_type,
            "client_id": self.oauth2_config.client_id,
            "redirect_uri": self.oauth2_config.redirect_uri,
            "scope": " ".join(self.oauth2_config.scopes),
            "state": state,
            "response_mode": self.oauth2_config.response_mode,
        }

        params.update(kwargs)

        return f"{self.oauth2_config.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "code": code,
            "client_id": self.oauth2_config.client_id,
            "client_secret": self.oauth2_config.client_secret,
            "redirect_uri": self.oauth2_config.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = await self.http_client.post(
            self.oauth2_config.token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to exchange code for token: {response.text}", provider=self.provider_name)

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider."""
        response = await self.http_client.get(
            self.oauth2_config.user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise SSOAuthError(f"Failed to get user info: {response.text}", provider=self.provider_name)

        return response.json()

    def map_user_data(self, user_data: Dict[str, Any]) -> SSOUser:
        """Map OAuth2 user data to SSOUser."""
        mapping = self.oauth2_config.user_mapping

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


def create_sso_provider(provider_name: str, config: Dict[str, Any]) -> SSOProvider:
    """
    Create SSO provider instance.

    Args:
        provider_name: Provider name
        config: Provider configuration

    Returns:
        SSO provider instance

    Raises:
        SSOUnsupportedProviderError: If provider is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "google":
        return GoogleSSOProvider(GoogleSSOConfig(**config))
    elif provider_name == "github":
        return GitHubSSOProvider(GitHubSSOConfig(**config))
    elif provider_name == "microsoft":
        return MicrosoftSSOProvider(MicrosoftSSOConfig(**config))
    elif provider_name == "apple":
        return AppleSSOProvider(AppleSSOConfig(**config))
    elif provider_name == "saml":
        return SAMLSSOProvider(SAMLSSOConfig(**config))
    elif provider_name == "generic_oauth2":
        return GenericOAuth2SSOProvider(GenericOAuth2SSOConfig(**config))
    else:
        raise SSOUnsupportedProviderError(provider_name)
