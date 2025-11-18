"""
OAuth2 authorization server implementation.

Provides a complete OAuth2 authorization server with all standard flows and endpoints.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

from .config import OAuth2Config
from .exceptions import (
    AccessDeniedError,
    InvalidClientError,
    InvalidGrantError,
    InvalidRequestError,
    InvalidScopeError,
    OAuth2Error,
    ServerError,
    UnsupportedGrantTypeError,
    UnsupportedResponseTypeError,
)
from .flows import FlowManager
from .models import (
    OAuth2AccessToken,
    OAuth2AuthorizationCode,
    OAuth2Client,
    OAuth2DeviceCode,
    OAuth2RefreshToken,
    generate_client_id,
    generate_client_secret,
)


class OAuth2Server:
    """
    OAuth2 authorization server.

    Provides complete OAuth2 authorization server functionality including
    all standard flows, endpoints, and security features.
    """

    def __init__(self, config: OAuth2Config) -> None:
        """
        Initialize OAuth2 server.

        Args:
            config: OAuth2 server configuration
        """
        self.config = config
        self.flow_manager = FlowManager(config)
        self.logger = logging.getLogger(__name__)

        # Storage backends (would be injected in real implementation)
        self._clients: Dict[str, OAuth2Client] = {}
        self._authorization_codes: Dict[str, OAuth2AuthorizationCode] = {}
        self._access_tokens: Dict[str, OAuth2AccessToken] = {}
        self._refresh_tokens: Dict[str, OAuth2RefreshToken] = {}
        self._device_codes: Dict[str, OAuth2DeviceCode] = {}

    # Client Management

    def create_client(
        self,
        client_name: str,
        client_type: str = "confidential",
        redirect_uris: Optional[List[str]] = None,
        grant_types: Optional[List[str]] = None,
        response_types: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> OAuth2Client:
        """
        Create new OAuth2 client.

        Args:
            client_name: Human-readable client name
            client_type: Client type (confidential or public)
            redirect_uris: Allowed redirect URIs
            grant_types: Allowed grant types
            response_types: Allowed response types
            scopes: Allowed scopes
            **kwargs: Additional client metadata

        Returns:
            Created OAuth2 client
        """
        # Generate client credentials
        client_id = generate_client_id()
        client_secret = generate_client_secret() if client_type == "confidential" else ""

        # Set defaults
        if redirect_uris is None:
            redirect_uris = []
        if grant_types is None:
            grant_types = self.config.supported_grant_types
        if response_types is None:
            response_types = self.config.supported_response_types
        if scopes is None:
            scopes = self.config.supported_scopes

        # Create client
        client = OAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            client_type=client_type,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            response_types=response_types,
            scopes=scopes,
            metadata=kwargs,
        )

        # Store client
        self._clients[client_id] = client

        self.logger.info(f"Created OAuth2 client: {client_id}")
        return client

    def get_client(self, client_id: str) -> Optional[OAuth2Client]:
        """Get OAuth2 client by ID."""
        return self._clients.get(client_id)

    def authenticate_client(self, client_id: str, client_secret: Optional[str] = None) -> OAuth2Client:
        """
        Authenticate OAuth2 client.

        Args:
            client_id: Client identifier
            client_secret: Client secret (required for confidential clients)

        Returns:
            Authenticated OAuth2 client

        Raises:
            InvalidClientError: If client authentication fails
        """
        client = self.get_client(client_id)
        if not client:
            raise InvalidClientError("Client not found")

        if not client.is_valid():
            raise InvalidClientError("Client is not valid")

        # For confidential clients, verify secret
        if client.client_type == "confidential":
            if not client_secret:
                raise InvalidClientError("Client secret required for confidential clients")
            if client.client_secret != client_secret:
                raise InvalidClientError("Invalid client secret")

        return client

    # Authorization Endpoint

    def handle_authorization_request(
        self,
        client_id: str,
        response_type: str,
        redirect_uri: str,
        scope: Optional[str] = None,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        nonce: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Handle authorization request.

        Args:
            client_id: Client identifier
            response_type: Response type
            redirect_uri: Redirect URI
            scope: Requested scopes
            state: State parameter
            code_challenge: PKCE code challenge
            code_challenge_method: PKCE code challenge method
            nonce: Nonce for OpenID Connect
            **kwargs: Additional parameters

        Returns:
            Authorization response data
        """
        try:
            # Get and validate client
            client = self.get_client(client_id)
            if not client:
                raise InvalidClientError("Client not found")

            # Validate authorization request
            validation_result = self.flow_manager.validate_authorization_request(
                client=client,
                response_type=response_type,
                redirect_uri=redirect_uri,
                scope=scope or "",
                state=state,
                **kwargs,
            )

            # Handle different response types
            if response_type == "code":
                return self._handle_authorization_code_request(
                    client=validation_result["client"],
                    redirect_uri=validation_result["redirect_uri"],
                    scopes=validation_result["scopes"],
                    state=validation_result["state"],
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    nonce=nonce,
                    **validation_result["extra"],
                )
            elif response_type == "token":
                return self._handle_implicit_request(
                    client=validation_result["client"],
                    redirect_uri=validation_result["redirect_uri"],
                    scopes=validation_result["scopes"],
                    state=validation_result["state"],
                    **validation_result["extra"],
                )
            else:
                raise UnsupportedResponseTypeError(f"Unsupported response type: {response_type}")

        except OAuth2Error as e:
            self.logger.error(f"Authorization request error: {e}")
            return self._create_error_response(e, redirect_uri, state)
        except Exception as e:
            self.logger.error(f"Unexpected error in authorization request: {e}")
            error = ServerError("An unexpected error occurred")
            return self._create_error_response(error, redirect_uri, state)

    def _handle_authorization_code_request(
        self,
        client: OAuth2Client,
        redirect_uri: str,
        scopes: List[str],
        state: Optional[str],
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        nonce: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Handle authorization code request."""
        # In a real implementation, this would redirect to a login page
        # For now, we'll create a mock authorization code

        # Create authorization code
        auth_code = self.flow_manager.flows["authorization_code"].create_authorization_code(
            client=client,
            user_id="mock_user_id",  # Would come from authentication
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
            **kwargs,
        )

        # Store authorization code
        self._authorization_codes[auth_code.code] = auth_code

        # Build redirect URI with authorization code
        params = {
            "code": auth_code.code,
        }
        if state:
            params["state"] = state

        redirect_url = f"{redirect_uri}?{urlencode(params)}"

        return {"type": "redirect", "url": redirect_url, "code": auth_code.code, "state": state}

    def _handle_implicit_request(
        self, client: OAuth2Client, redirect_uri: str, scopes: List[str], state: Optional[str], **kwargs: Any
    ) -> Dict[str, Any]:
        """Handle implicit flow request."""
        if not self.config.allow_implicit_grant:
            raise UnsupportedResponseTypeError("Implicit grant is not allowed")

        # Create access token
        access_token = self.flow_manager.flows["implicit"].create_access_token(
            client=client,
            user_id="mock_user_id",  # Would come from authentication
            scopes=scopes,
            **kwargs,
        )

        # Store access token
        self._access_tokens[access_token.token] = access_token

        # Build redirect URI with access token
        params = {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
        }
        if state:
            params["state"] = state

        redirect_url = f"{redirect_uri}#{urlencode(params)}"

        return {
            "type": "redirect",
            "url": redirect_url,
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "state": state,
        }

    # Token Endpoint

    def handle_token_request(
        self,
        grant_type: str,
        client_id: str,
        client_secret: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_verifier: Optional[str] = None,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        device_code: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Handle token request.

        Args:
            grant_type: Grant type
            client_id: Client identifier
            client_secret: Client secret
            code: Authorization code
            redirect_uri: Redirect URI
            code_verifier: PKCE code verifier
            refresh_token: Refresh token
            scope: Requested scopes
            username: Username (for password flow)
            password: Password (for password flow)
            device_code: Device code (for device flow)
            **kwargs: Additional parameters

        Returns:
            Token response data
        """
        try:
            # Authenticate client
            client = self.authenticate_client(client_id, client_secret)

            # Validate token request
            validation_result = self.flow_manager.validate_token_request(client=client, grant_type=grant_type, **kwargs)

            # Handle different grant types
            if grant_type == "authorization_code":
                return self._handle_authorization_code_grant(
                    client=client, code=code, redirect_uri=redirect_uri, code_verifier=code_verifier, scope=scope
                )
            elif grant_type == "client_credentials":
                return self._handle_client_credentials_grant(client=client, scope=scope)
            elif grant_type == "refresh_token":
                return self._handle_refresh_token_grant(client=client, refresh_token=refresh_token, scope=scope)
            elif grant_type == "device_code":
                return self._handle_device_code_grant(client=client, device_code=device_code)
            elif grant_type == "password":
                return self._handle_password_grant(client=client, username=username, password=password, scope=scope)
            else:
                raise UnsupportedGrantTypeError(f"Unsupported grant type: {grant_type}")

        except OAuth2Error as e:
            self.logger.error(f"Token request error: {e}")
            return e.to_dict()
        except Exception as e:
            self.logger.error(f"Unexpected error in token request: {e}")
            return ServerError("An unexpected error occurred").to_dict()

    def _handle_authorization_code_grant(
        self, client: OAuth2Client, code: str, redirect_uri: str, code_verifier: Optional[str], scope: Optional[str]
    ) -> Dict[str, Any]:
        """Handle authorization code grant."""
        if not code:
            raise InvalidRequestError("Authorization code is required")

        # Get authorization code
        auth_code = self._authorization_codes.get(code)
        if not auth_code:
            raise InvalidGrantError("Invalid authorization code")

        # Validate authorization code
        if not auth_code.is_valid():
            raise InvalidGrantError("Authorization code is invalid or expired")

        if auth_code.client_id != client.client_id:
            raise InvalidGrantError("Authorization code was issued to a different client")

        if auth_code.redirect_uri != redirect_uri:
            raise InvalidGrantError("Redirect URI mismatch")

        # Validate PKCE if present
        if auth_code.code_challenge:
            if not code_verifier:
                raise InvalidRequestError("Code verifier is required for PKCE")

            if not self.flow_manager.pkce_flow.validate_code_challenge(
                auth_code.code_challenge, code_verifier, auth_code.code_challenge_method or "S256"
            ):
                raise InvalidGrantError("Invalid code verifier")

        # Mark authorization code as used
        auth_code.mark_as_used()

        # Create access token
        access_token = self.flow_manager.flows["authorization_code"].create_access_token(
            client=client, user_id=auth_code.user_id, scopes=auth_code.scopes, metadata={"authorization_code": code}
        )

        # Create refresh token
        refresh_token = self.flow_manager.flows["refresh_token"].create_refresh_token(
            client=client, user_id=auth_code.user_id, scopes=auth_code.scopes, metadata={"authorization_code": code}
        )

        # Store tokens
        self._access_tokens[access_token.token] = access_token
        self._refresh_tokens[refresh_token.token] = refresh_token

        return {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "refresh_token": refresh_token.token,
            "scope": " ".join(access_token.scopes),
        }

    def _handle_client_credentials_grant(self, client: OAuth2Client, scope: Optional[str]) -> Dict[str, Any]:
        """Handle client credentials grant."""
        # Validate scopes
        scopes = self.flow_manager.flows["client_credentials"].validate_scope(scope or "", client)

        # Create access token
        access_token = self.flow_manager.flows["client_credentials"].create_access_token(client=client, scopes=scopes)

        # Store access token
        self._access_tokens[access_token.token] = access_token

        return {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "scope": " ".join(access_token.scopes),
        }

    def _handle_refresh_token_grant(
        self, client: OAuth2Client, refresh_token: str, scope: Optional[str]
    ) -> Dict[str, Any]:
        """Handle refresh token grant."""
        if not refresh_token:
            raise InvalidRequestError("Refresh token is required")

        # Get refresh token
        token = self._refresh_tokens.get(refresh_token)
        if not token:
            raise InvalidGrantError("Invalid refresh token")

        # Validate refresh token
        if not token.is_valid():
            raise InvalidGrantError("Refresh token is invalid or expired")

        if token.client_id != client.client_id:
            raise InvalidGrantError("Refresh token was issued to a different client")

        # Validate requested scopes
        requested_scopes = scope.split() if scope else token.scopes
        if not all(s in token.scopes for s in requested_scopes):
            raise InvalidScopeError("Requested scope exceeds granted scope")

        # Create new access token
        access_token = self.flow_manager.flows["authorization_code"].create_access_token(
            client=client, user_id=token.user_id, scopes=requested_scopes, metadata={"refresh_token": refresh_token}
        )

        # Create new refresh token
        new_refresh_token = self.flow_manager.flows["refresh_token"].create_refresh_token(
            client=client,
            user_id=token.user_id,
            scopes=requested_scopes,
            metadata={"previous_refresh_token": refresh_token},
        )

        # Revoke old refresh token
        token.revoke()

        # Store new tokens
        self._access_tokens[access_token.token] = access_token
        self._refresh_tokens[new_refresh_token.token] = new_refresh_token

        return {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "refresh_token": new_refresh_token.token,
            "scope": " ".join(access_token.scopes),
        }

    def _handle_device_code_grant(self, client: OAuth2Client, device_code: str) -> Dict[str, Any]:
        """Handle device code grant."""
        if not device_code:
            raise InvalidRequestError("Device code is required")

        # Get device code
        device = self._device_codes.get(device_code)
        if not device:
            raise InvalidGrantError("Invalid device code")

        # Validate device code
        if not device.is_valid():
            raise InvalidGrantError("Device code is invalid or expired")

        if device.client_id != client.client_id:
            raise InvalidGrantError("Device code was issued to a different client")

        if not device.is_authorized:
            raise InvalidGrantError("Device code not yet authorized")

        # Create access token
        access_token = self.flow_manager.flows["authorization_code"].create_access_token(
            client=client, user_id=device.user_id, scopes=device.scopes, metadata={"device_code": device_code}
        )

        # Create refresh token
        refresh_token = self.flow_manager.flows["refresh_token"].create_refresh_token(
            client=client, user_id=device.user_id, scopes=device.scopes, metadata={"device_code": device_code}
        )

        # Store tokens
        self._access_tokens[access_token.token] = access_token
        self._refresh_tokens[refresh_token.token] = refresh_token

        return {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "refresh_token": refresh_token.token,
            "scope": " ".join(access_token.scopes),
        }

    def _handle_password_grant(
        self, client: OAuth2Client, username: str, password: str, scope: Optional[str]
    ) -> Dict[str, Any]:
        """Handle password grant."""
        if not username or not password:
            raise InvalidRequestError("Username and password are required")

        # In a real implementation, this would authenticate the user
        # For now, we'll use a mock user ID
        user_id = "mock_user_id"

        # Validate scopes
        scopes = self.flow_manager.flows["password"].validate_scope(scope or "", client)

        # Create tokens
        access_token, refresh_token = self.flow_manager.flows["password"].create_access_token(
            client=client, user_id=user_id, scopes=scopes, metadata={"username": username}
        )

        # Store tokens
        self._access_tokens[access_token.token] = access_token
        self._refresh_tokens[refresh_token.token] = refresh_token

        return {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": self.config.access_token_lifetime,
            "refresh_token": refresh_token.token,
            "scope": " ".join(access_token.scopes),
        }

    # Utility Methods

    def _create_error_response(self, error: OAuth2Error, redirect_uri: str, state: Optional[str]) -> Dict[str, Any]:
        """Create error response for authorization endpoint."""
        params = error.to_dict()
        if state:
            params["state"] = state

        redirect_url = f"{redirect_uri}?{urlencode(params)}"

        return {
            "type": "redirect",
            "url": redirect_url,
            "error": error.error,
            "error_description": error.description,
            "state": state,
        }

    def get_access_token(self, token: str) -> Optional[OAuth2AccessToken]:
        """Get access token by value."""
        return self._access_tokens.get(token)

    def revoke_access_token(self, token: str) -> bool:
        """Revoke access token."""
        access_token = self._access_tokens.get(token)
        if access_token:
            access_token.revoke()
            return True
        return False

    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke refresh token."""
        refresh_token = self._refresh_tokens.get(token)
        if refresh_token:
            refresh_token.revoke()
            return True
        return False

    def introspect_token(self, token: str) -> Dict[str, Any]:
        """Introspect token and return metadata."""
        access_token = self._access_tokens.get(token)
        if access_token and access_token.is_valid():
            return {
                "active": True,
                "client_id": access_token.client_id,
                "user_id": access_token.user_id,
                "scope": " ".join(access_token.scopes),
                "token_type": access_token.token_type,
                "exp": int(access_token.expires_at.timestamp()),
                "iat": int(access_token.created_at.timestamp()),
            }
        else:
            return {"active": False}
