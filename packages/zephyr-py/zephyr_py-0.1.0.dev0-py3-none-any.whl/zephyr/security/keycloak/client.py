"""
Keycloak OAuth2/OIDC client implementation.

Provides OAuth2/OIDC authentication flow, token operations, and user info retrieval.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError

from .config import KeycloakConfig
from .exceptions import (
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakExpiredTokenError,
    KeycloakInvalidTokenError,
    KeycloakTokenError,
)
from .models import KeycloakToken, KeycloakUserInfo


class KeycloakClient:
    """Keycloak OAuth2/OIDC client."""

    def __init__(self, config: KeycloakConfig) -> None:
        """
        Initialize Keycloak client.

        Args:
            config: Keycloak configuration
        """
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=config.timeout, verify=config.verify_ssl)
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_time: datetime | None = None

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self) -> "KeycloakClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    def get_authorization_url(
        self, redirect_uri: str, state: str | None = None, scopes: list[str] | None = None, **kwargs: Any
    ) -> str:
        """
        Get OAuth2 authorization URL.

        Args:
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection
            scopes: OAuth2 scopes (defaults to config scopes)
            **kwargs: Additional query parameters

        Returns:
            Authorization URL
        """
        if scopes is None:
            scopes = self.config.default_scopes

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
        }

        if state:
            params["state"] = state

        params.update(kwargs)

        return f"{self.config.get_authorization_endpoint()}?{urlencode(params)}"

    async def exchange_code_for_token(
        self, code: str, redirect_uri: str, code_verifier: str | None = None
    ) -> KeycloakToken:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization request
            code_verifier: PKCE code verifier

        Returns:
            Token response

        Raises:
            KeycloakAuthenticationError: If token exchange fails
            KeycloakConnectionError: If connection fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.config.client_id,
        }

        if not self.config.public_client and self.config.client_secret:
            data["client_secret"] = self.config.client_secret

        if code_verifier:
            data["code_verifier"] = code_verifier

        try:
            response = await self.http_client.post(
                self.config.get_token_endpoint(),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                raise KeycloakAuthenticationError(f"Token exchange failed: {response.text}", response.status_code)

            token_data = response.json()
            return KeycloakToken(**token_data)

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> KeycloakToken:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New token response

        Raises:
            KeycloakTokenError: If token refresh fails
            KeycloakConnectionError: If connection fails
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
        }

        if not self.config.public_client and self.config.client_secret:
            data["client_secret"] = self.config.client_secret

        try:
            response = await self.http_client.post(
                self.config.get_token_endpoint(),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                raise KeycloakTokenError(f"Token refresh failed: {response.text}", response.status_code)

            token_data = response.json()
            return KeycloakToken(**token_data)

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def get_user_info(self, access_token: str) -> KeycloakUserInfo:
        """
        Get user information from UserInfo endpoint.

        Args:
            access_token: Access token

        Returns:
            User information

        Raises:
            KeycloakAuthenticationError: If request fails
            KeycloakConnectionError: If connection fails
        """
        try:
            response = await self.http_client.get(
                self.config.get_userinfo_endpoint(), headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise KeycloakAuthenticationError(f"Failed to get user info: {response.text}", response.status_code)

            user_data = response.json()
            return KeycloakUserInfo(**user_data)

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def logout(self, refresh_token: str, redirect_uri: str | None = None) -> None:
        """
        Logout user and invalidate tokens.

        Args:
            refresh_token: Refresh token to invalidate
            redirect_uri: Optional redirect URI after logout

        Raises:
            KeycloakAuthenticationError: If logout fails
            KeycloakConnectionError: If connection fails
        """
        data = {
            "client_id": self.config.client_id,
            "refresh_token": refresh_token,
        }

        if not self.config.public_client and self.config.client_secret:
            data["client_secret"] = self.config.client_secret

        if redirect_uri:
            data["redirect_uri"] = redirect_uri

        try:
            response = await self.http_client.post(
                self.config.get_end_session_endpoint(),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code not in (200, 204):
                raise KeycloakAuthenticationError(f"Logout failed: {response.text}", response.status_code)

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def introspect_token(self, token: str) -> dict[str, Any]:
        """
        Introspect token to check validity and get metadata.

        Args:
            token: Token to introspect

        Returns:
            Token introspection result

        Raises:
            KeycloakTokenError: If introspection fails
            KeycloakConnectionError: If connection fails
        """
        data = {
            "token": token,
            "client_id": self.config.client_id,
        }

        if not self.config.public_client and self.config.client_secret:
            data["client_secret"] = self.config.client_secret

        try:
            response = await self.http_client.post(
                self.config.get_introspection_endpoint(),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                raise KeycloakTokenError(f"Token introspection failed: {response.text}", response.status_code)

            return response.json()

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def get_jwks(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        Get JWKS (JSON Web Key Set) for token validation.

        Args:
            force_refresh: Force refresh of cached JWKS

        Returns:
            JWKS data

        Raises:
            KeycloakConnectionError: If fetching JWKS fails
        """
        # Check cache
        if not force_refresh and self._jwks_cache and self._jwks_cache_time:
            cache_age = (datetime.utcnow() - self._jwks_cache_time).total_seconds()
            if cache_age < 3600:  # Cache for 1 hour
                return self._jwks_cache

        try:
            response = await self.http_client.get(self.config.get_jwks_uri())

            if response.status_code != 200:
                raise KeycloakConnectionError(f"Failed to fetch JWKS: {response.text}")

            self._jwks_cache = response.json()
            self._jwks_cache_time = datetime.utcnow()
            return self._jwks_cache

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def validate_token(
        self,
        token: str,
        verify_signature: bool | None = None,
        verify_audience: bool | None = None,
        verify_expiry: bool | None = None,
    ) -> dict[str, Any]:
        """
        Validate JWT token.

        Args:
            token: JWT token to validate
            verify_signature: Verify token signature (defaults to config)
            verify_audience: Verify audience claim (defaults to config)
            verify_expiry: Verify expiry (defaults to config)

        Returns:
            Decoded token claims

        Raises:
            KeycloakInvalidTokenError: If token is invalid
            KeycloakExpiredTokenError: If token is expired
        """
        if verify_signature is None:
            verify_signature = self.config.verify_token_signature
        if verify_audience is None:
            verify_audience = self.config.verify_token_audience
        if verify_expiry is None:
            verify_expiry = self.config.verify_token_expiry

        try:
            # Get JWKS for signature verification
            if verify_signature:
                jwks = await self.get_jwks()
                options = {
                    "verify_signature": True,
                    "verify_aud": verify_audience,
                    "verify_exp": verify_expiry,
                }

                # Decode with verification
                claims = jwt.decode(
                    token,
                    jwks,
                    options=options,
                    audience=self.config.client_id if verify_audience else None,
                    leeway=self.config.token_leeway,
                )
            else:
                # Decode without verification
                claims = jwt.get_unverified_claims(token)

            return claims

        except ExpiredSignatureError:
            raise KeycloakExpiredTokenError("Token has expired")
        except JWTError as e:
            raise KeycloakInvalidTokenError(f"Invalid token: {str(e)}")

    def generate_pkce_challenge(self, code_verifier: str | None = None) -> tuple[str, str]:
        """
        Generate PKCE code challenge and verifier.

        Args:
            code_verifier: Optional code verifier (generated if not provided)

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        if not code_verifier:
            code_verifier = secrets.token_urlsafe(64)

        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge_b64 = secrets.token_urlsafe(len(code_challenge))

        return code_verifier, code_challenge_b64

    async def get_well_known_config(self) -> dict[str, Any]:
        """
        Get OpenID Connect discovery configuration.

        Returns:
            Well-known configuration

        Raises:
            KeycloakConnectionError: If fetching configuration fails
        """
        try:
            response = await self.http_client.get(self.config.get_well_known_url())

            if response.status_code != 200:
                raise KeycloakConnectionError(f"Failed to fetch well-known config: {response.text}")

            return response.json()

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")
