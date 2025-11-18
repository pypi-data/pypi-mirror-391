"""
OAuth2 authorization flows implementation.

Implements all OAuth2 authorization flows including Authorization Code,
Client Credentials, PKCE, Device, and Refresh Token flows.
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse

from .config import OAuth2Config
from .exceptions import (
    AccessDeniedError,
    DeviceCodeExpiredError,
    DeviceCodePendingError,
    DeviceCodeSlowDownError,
    DeviceCodeAccessDeniedError,
    InvalidClientError,
    InvalidCodeChallengeError,
    InvalidCodeVerifierError,
    InvalidGrantError,
    InvalidRedirectUriError,
    InvalidRequestError,
    InvalidScopeError,
    UnsupportedGrantTypeError,
)
from .models import (
    OAuth2AccessToken,
    OAuth2AuthorizationCode,
    OAuth2Client,
    OAuth2DeviceCode,
    OAuth2RefreshToken,
    generate_access_token,
    generate_authorization_code,
    generate_device_code,
    generate_refresh_token,
    generate_user_code,
)


class BaseFlow:
    """Base class for OAuth2 flows."""

    def __init__(self, config: OAuth2Config) -> None:
        """Initialize flow with configuration."""
        self.config = config

    def validate_client(self, client: OAuth2Client, grant_type: str) -> None:
        """Validate client for grant type."""
        if not client.is_valid():
            raise InvalidClientError("Client is not valid")

        if not client.is_grant_type_allowed(grant_type):
            raise UnsupportedGrantTypeError(f"Grant type '{grant_type}' not allowed for this client")

    def validate_scope(self, requested_scope: str, client: OAuth2Client) -> List[str]:
        """Validate and return scopes."""
        if not requested_scope:
            return self.config.default_scopes

        scopes = requested_scope.split()

        # Check if all scopes are supported
        if not self.config.is_scope_supported(requested_scope):
            raise InvalidScopeError(f"Unsupported scope: {requested_scope}")

        # Check if client is allowed to request these scopes
        if not client.is_scope_allowed(requested_scope):
            raise InvalidScopeError(f"Client not allowed to request scope: {requested_scope}")

        return scopes

    def validate_redirect_uri(self, redirect_uri: str, client: OAuth2Client) -> None:
        """Validate redirect URI."""
        if not client.is_redirect_uri_allowed(redirect_uri):
            raise InvalidRedirectUriError("Redirect URI not allowed for this client")


class AuthorizationCodeFlow(BaseFlow):
    """Authorization Code flow implementation."""

    def create_authorization_code(
        self,
        client: OAuth2Client,
        user_id: str,
        redirect_uri: str,
        scopes: List[str],
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        nonce: Optional[str] = None,
        **kwargs: Any,
    ) -> OAuth2AuthorizationCode:
        """Create authorization code."""
        self.validate_client(client, "authorization_code")
        self.validate_redirect_uri(redirect_uri, client)

        # Generate authorization code
        code = generate_authorization_code()

        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.authorization_code_lifetime)

        return OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
            expires_at=expires_at,
            metadata=kwargs,
        )

    def exchange_code_for_tokens(
        self, code: str, client: OAuth2Client, redirect_uri: str, code_verifier: Optional[str] = None, **kwargs: Any
    ) -> Tuple[OAuth2AccessToken, Optional[OAuth2RefreshToken]]:
        """Exchange authorization code for tokens."""
        # This would typically look up the authorization code from storage
        # For now, we'll create a mock implementation
        raise NotImplementedError("This would be implemented with actual storage backend")

    def validate_code_verifier(self, code_challenge: str, code_verifier: str, method: str) -> bool:
        """Validate PKCE code verifier."""
        if method == "plain":
            return code_challenge == code_verifier
        elif method == "S256":
            challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
            challenge_b64 = secrets.token_urlsafe(len(challenge))
            return code_challenge == challenge_b64
        else:
            raise InvalidCodeChallengeError(f"Unsupported code challenge method: {method}")


class ClientCredentialsFlow(BaseFlow):
    """Client Credentials flow implementation."""

    def create_access_token(self, client: OAuth2Client, scopes: List[str], **kwargs: Any) -> OAuth2AccessToken:
        """Create access token for client credentials flow."""
        self.validate_client(client, "client_credentials")

        # Generate access token
        token = generate_access_token()

        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.access_token_lifetime)

        return OAuth2AccessToken(
            token=token,
            token_type=self.config.access_token_type,
            client_id=client.client_id,
            user_id=None,  # No user in client credentials flow
            scopes=scopes,
            expires_at=expires_at,
            metadata=kwargs,
        )


class PKCEFlow(BaseFlow):
    """PKCE (Proof Key for Code Exchange) flow implementation."""

    def generate_code_challenge(self, code_verifier: str, method: str = "S256") -> str:
        """Generate code challenge from code verifier."""
        if method not in self.config.supported_code_challenge_methods:
            raise InvalidCodeChallengeError(f"Unsupported code challenge method: {method}")

        if method == "plain":
            return code_verifier
        elif method == "S256":
            challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
            return secrets.token_urlsafe(len(challenge))
        else:
            raise InvalidCodeChallengeError(f"Invalid code challenge method: {method}")

    def generate_code_verifier(self, length: int = 128) -> str:
        """Generate code verifier."""
        return secrets.token_urlsafe(length)

    def validate_code_challenge(self, code_challenge: str, code_verifier: str, method: str) -> bool:
        """Validate code challenge against code verifier."""
        if method not in self.config.supported_code_challenge_methods:
            raise InvalidCodeChallengeError(f"Unsupported code challenge method: {method}")

        if method == "plain":
            return code_challenge == code_verifier
        elif method == "S256":
            challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
            challenge_b64 = secrets.token_urlsafe(len(challenge))
            return code_challenge == challenge_b64
        else:
            return False


class DeviceFlow(BaseFlow):
    """Device Authorization flow implementation."""

    def create_device_code(self, client: OAuth2Client, scopes: List[str], **kwargs: Any) -> OAuth2DeviceCode:
        """Create device code for device flow."""
        self.validate_client(client, "device_code")

        # Generate device code and user code
        device_code = generate_device_code()
        user_code = generate_user_code()

        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.device_code_lifetime)

        return OAuth2DeviceCode(
            device_code=device_code,
            user_code=user_code,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=expires_at,
            interval=self.config.device_code_interval,
            metadata=kwargs,
        )

    def poll_device_code(self, device_code: str) -> Dict[str, Any]:
        """Poll device code for authorization status."""
        # This would typically look up the device code from storage
        # For now, we'll create a mock implementation
        raise NotImplementedError("This would be implemented with actual storage backend")

    def authorize_device_code(self, device_code: str, user_id: str) -> None:
        """Authorize device code for user."""
        # This would typically update the device code in storage
        # For now, we'll create a mock implementation
        raise NotImplementedError("This would be implemented with actual storage backend")


class RefreshTokenFlow(BaseFlow):
    """Refresh Token flow implementation."""

    def create_refresh_token(
        self, client: OAuth2Client, user_id: str, scopes: List[str], **kwargs: Any
    ) -> OAuth2RefreshToken:
        """Create refresh token."""
        self.validate_client(client, "refresh_token")

        # Generate refresh token
        token = generate_refresh_token()

        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.refresh_token_lifetime)

        return OAuth2RefreshToken(
            token=token,
            client_id=client.client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
            metadata=kwargs,
        )

    def refresh_access_token(
        self, refresh_token: str, client: OAuth2Client, requested_scopes: Optional[List[str]] = None, **kwargs: Any
    ) -> Tuple[OAuth2AccessToken, OAuth2RefreshToken]:
        """Refresh access token using refresh token."""
        # This would typically look up the refresh token from storage
        # For now, we'll create a mock implementation
        raise NotImplementedError("This would be implemented with actual storage backend")

    def revoke_refresh_token(self, refresh_token: str) -> None:
        """Revoke refresh token."""
        # This would typically update the refresh token in storage
        # For now, we'll create a mock implementation
        raise NotImplementedError("This would be implemented with actual storage backend")


class ImplicitFlow(BaseFlow):
    """Implicit flow implementation (deprecated but still supported)."""

    def create_access_token(
        self, client: OAuth2Client, user_id: str, scopes: List[str], **kwargs: Any
    ) -> OAuth2AccessToken:
        """Create access token for implicit flow."""
        if not self.config.allow_implicit_grant:
            raise UnsupportedGrantTypeError("Implicit grant is not allowed")

        self.validate_client(client, "implicit")

        # Generate access token
        token = generate_access_token()

        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.access_token_lifetime)

        return OAuth2AccessToken(
            token=token,
            token_type=self.config.access_token_type,
            client_id=client.client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
            metadata=kwargs,
        )


class PasswordFlow(BaseFlow):
    """Password flow implementation (deprecated but still supported)."""

    def create_access_token(
        self, client: OAuth2Client, user_id: str, scopes: List[str], **kwargs: Any
    ) -> Tuple[OAuth2AccessToken, OAuth2RefreshToken]:
        """Create access and refresh tokens for password flow."""
        self.validate_client(client, "password")

        # Generate tokens
        access_token = generate_access_token()
        refresh_token = generate_refresh_token()

        # Set expiration times
        access_expires_at = datetime.utcnow() + timedelta(seconds=self.config.access_token_lifetime)
        refresh_expires_at = datetime.utcnow() + timedelta(seconds=self.config.refresh_token_lifetime)

        access_token_obj = OAuth2AccessToken(
            token=access_token,
            token_type=self.config.access_token_type,
            client_id=client.client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=access_expires_at,
            metadata=kwargs,
        )

        refresh_token_obj = OAuth2RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=refresh_expires_at,
            metadata=kwargs,
        )

        return access_token_obj, refresh_token_obj


class FlowManager:
    """Manages all OAuth2 flows."""

    def __init__(self, config: OAuth2Config) -> None:
        """Initialize flow manager."""
        self.config = config
        self.flows = {
            "authorization_code": AuthorizationCodeFlow(config),
            "client_credentials": ClientCredentialsFlow(config),
            "device_code": DeviceFlow(config),
            "refresh_token": RefreshTokenFlow(config),
            "implicit": ImplicitFlow(config),
            "password": PasswordFlow(config),
        }
        self.pkce_flow = PKCEFlow(config)

    def get_flow(self, grant_type: str) -> BaseFlow:
        """Get flow for grant type."""
        if grant_type not in self.flows:
            raise UnsupportedGrantTypeError(f"Unsupported grant type: {grant_type}")
        return self.flows[grant_type]

    def is_grant_type_supported(self, grant_type: str) -> bool:
        """Check if grant type is supported."""
        return grant_type in self.flows and self.config.is_grant_type_supported(grant_type)

    def is_response_type_supported(self, response_type: str) -> bool:
        """Check if response type is supported."""
        return self.config.is_response_type_supported(response_type)

    def validate_authorization_request(
        self,
        client: OAuth2Client,
        response_type: str,
        redirect_uri: str,
        scope: str,
        state: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate authorization request."""
        # Validate response type
        if not self.is_response_type_supported(response_type):
            raise UnsupportedGrantTypeError(f"Unsupported response type: {response_type}")

        # Validate client
        if not client.is_valid():
            raise InvalidClientError("Client is not valid")

        # Validate redirect URI
        if not client.is_redirect_uri_allowed(redirect_uri):
            raise InvalidRedirectUriError("Redirect URI not allowed for this client")

        # Validate scopes
        scopes = self.flows["authorization_code"].validate_scope(scope, client)

        return {
            "client": client,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
            "scopes": scopes,
            "state": state,
            "extra": kwargs,
        }

    def validate_token_request(self, client: OAuth2Client, grant_type: str, **kwargs: Any) -> Dict[str, Any]:
        """Validate token request."""
        # Validate grant type
        if not self.is_grant_type_supported(grant_type):
            raise UnsupportedGrantTypeError(f"Unsupported grant type: {grant_type}")

        # Validate client
        if not client.is_valid():
            raise InvalidClientError("Client is not valid")

        # Get flow and validate
        flow = self.get_flow(grant_type)
        flow.validate_client(client, grant_type)

        return {"client": client, "grant_type": grant_type, "flow": flow, "extra": kwargs}
