"""
OAuth2 endpoint implementations.

Provides ASGI-compatible OAuth2 endpoints for authorization, token, revocation, and introspection.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from .config import OAuth2Config
from .exceptions import InvalidRequestError, OAuth2Error
from .server import OAuth2Server


class BaseEndpoint:
    """Base class for OAuth2 endpoints."""

    def __init__(self, server: OAuth2Server) -> None:
        """Initialize endpoint with OAuth2 server."""
        self.server = server
        self.config = server.config
        self.logger = logging.getLogger(__name__)

    def _parse_query_params(self, query_string: bytes) -> Dict[str, List[str]]:
        """Parse query string parameters."""
        if not query_string:
            return {}
        return parse_qs(query_string.decode("utf-8"))

    def _parse_form_data(self, body: bytes) -> Dict[str, List[str]]:
        """Parse form data from request body."""
        if not body:
            return {}
        return parse_qs(body.decode("utf-8"))

    def _create_response(
        self, status: int, headers: Dict[str, str], body: str, content_type: str = "application/json"
    ) -> Dict[str, Any]:
        """Create ASGI response."""
        return {
            "type": "http.response.start",
            "status": status,
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        }, {
            "type": "http.response.body",
            "body": body.encode("utf-8"),
        }

    def _create_json_response(
        self, data: Dict[str, Any], status: int = 200, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create JSON response."""
        if headers is None:
            headers = {}

        headers["Content-Type"] = "application/json"
        headers["Cache-Control"] = "no-store"
        headers["Pragma"] = "no-cache"

        body = json.dumps(data, indent=2)
        return self._create_response(status, headers, body)

    def _create_error_response(
        self, error: OAuth2Error, status: int = 400, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create error response."""
        return self._create_json_response(error.to_dict(), status, headers)

    def _create_redirect_response(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create redirect response."""
        if headers is None:
            headers = {}

        headers["Location"] = url

        return self._create_response(302, headers, "")


class AuthorizationEndpoint(BaseEndpoint):
    """OAuth2 authorization endpoint."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle authorization request."""
        try:
            # Parse request
            query_params = self._parse_query_params(scope.get("query_string", b""))

            # Extract parameters
            client_id = query_params.get("client_id", [None])[0]
            response_type = query_params.get("response_type", [None])[0]
            redirect_uri = query_params.get("redirect_uri", [None])[0]
            scope_param = query_params.get("scope", [None])[0]
            state = query_params.get("state", [None])[0]
            code_challenge = query_params.get("code_challenge", [None])[0]
            code_challenge_method = query_params.get("code_challenge_method", [None])[0]
            nonce = query_params.get("nonce", [None])[0]

            # Validate required parameters
            if not client_id:
                raise InvalidRequestError("client_id is required")
            if not response_type:
                raise InvalidRequestError("response_type is required")
            if not redirect_uri:
                raise InvalidRequestError("redirect_uri is required")

            # Handle authorization request
            result = self.server.handle_authorization_request(
                client_id=client_id,
                response_type=response_type,
                redirect_uri=redirect_uri,
                scope=scope_param,
                state=state,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                nonce=nonce,
            )

            # Send response
            if result["type"] == "redirect":
                response = self._create_redirect_response(result["url"])
                await send(response[0])
                await send(response[1])
            else:
                response = self._create_json_response(result)
                await send(response[0])
                await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"Authorization endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in authorization endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class TokenEndpoint(BaseEndpoint):
    """OAuth2 token endpoint."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle token request."""
        try:
            # Parse request
            query_params = self._parse_query_params(scope.get("query_string", b""))

            # Get request body
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
                elif message["type"] == "http.disconnect":
                    return

            # Parse form data
            form_data = self._parse_form_data(body)

            # Extract parameters
            grant_type = form_data.get("grant_type", [None])[0]
            client_id = form_data.get("client_id", [None])[0]
            client_secret = form_data.get("client_secret", [None])[0]
            code = form_data.get("code", [None])[0]
            redirect_uri = form_data.get("redirect_uri", [None])[0]
            code_verifier = form_data.get("code_verifier", [None])[0]
            refresh_token = form_data.get("refresh_token", [None])[0]
            scope_param = form_data.get("scope", [None])[0]
            username = form_data.get("username", [None])[0]
            password = form_data.get("password", [None])[0]
            device_code = form_data.get("device_code", [None])[0]

            # Validate required parameters
            if not grant_type:
                raise InvalidRequestError("grant_type is required")
            if not client_id:
                raise InvalidRequestError("client_id is required")

            # Handle token request
            result = self.server.handle_token_request(
                grant_type=grant_type,
                client_id=client_id,
                client_secret=client_secret,
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier,
                refresh_token=refresh_token,
                scope=scope_param,
                username=username,
                password=password,
                device_code=device_code,
            )

            # Send response
            response = self._create_json_response(result)
            await send(response[0])
            await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"Token endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in token endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class RevocationEndpoint(BaseEndpoint):
    """OAuth2 token revocation endpoint."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle token revocation request."""
        try:
            # Parse request
            query_params = self._parse_query_params(scope.get("query_string", b""))

            # Get request body
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
                elif message["type"] == "http.disconnect":
                    return

            # Parse form data
            form_data = self._parse_form_data(body)

            # Extract parameters
            token = form_data.get("token", [None])[0]
            token_type_hint = form_data.get("token_type_hint", [None])[0]
            client_id = form_data.get("client_id", [None])[0]
            client_secret = form_data.get("client_secret", [None])[0]

            # Validate required parameters
            if not token:
                raise InvalidRequestError("token is required")

            # Authenticate client
            if client_id:
                self.server.authenticate_client(client_id, client_secret)

            # Revoke token
            revoked = False
            if token_type_hint == "access_token" or not token_type_hint:
                revoked = self.server.revoke_access_token(token)
            if token_type_hint == "refresh_token" or not token_type_hint:
                revoked = revoked or self.server.revoke_refresh_token(token)

            # Send response
            response = self._create_json_response({}, 200)
            await send(response[0])
            await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"Revocation endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in revocation endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class IntrospectionEndpoint(BaseEndpoint):
    """OAuth2 token introspection endpoint."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle token introspection request."""
        try:
            # Parse request
            query_params = self._parse_query_params(scope.get("query_string", b""))

            # Get request body
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
                elif message["type"] == "http.disconnect":
                    return

            # Parse form data
            form_data = self._parse_form_data(body)

            # Extract parameters
            token = form_data.get("token", [None])[0]
            token_type_hint = form_data.get("token_type_hint", [None])[0]
            client_id = form_data.get("client_id", [None])[0]
            client_secret = form_data.get("client_secret", [None])[0]

            # Validate required parameters
            if not token:
                raise InvalidRequestError("token is required")

            # Authenticate client
            if client_id:
                self.server.authenticate_client(client_id, client_secret)

            # Introspect token
            result = self.server.introspect_token(token)

            # Send response
            response = self._create_json_response(result)
            await send(response[0])
            await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"Introspection endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in introspection endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class DeviceAuthorizationEndpoint(BaseEndpoint):
    """OAuth2 device authorization endpoint."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle device authorization request."""
        try:
            # Parse request
            query_params = self._parse_query_params(scope.get("query_string", b""))

            # Get request body
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
                elif message["type"] == "http.disconnect":
                    return

            # Parse form data
            form_data = self._parse_form_data(body)

            # Extract parameters
            client_id = form_data.get("client_id", [None])[0]
            scope_param = form_data.get("scope", [None])[0]

            # Validate required parameters
            if not client_id:
                raise InvalidRequestError("client_id is required")

            # Get client
            client = self.server.get_client(client_id)
            if not client:
                from .exceptions import InvalidClientError

                raise InvalidClientError("Client not found")

            # Create device code
            device_code = self.server.flow_manager.flows["device_code"].create_device_code(
                client=client, scopes=scope_param.split() if scope_param else []
            )

            # Store device code
            self.server._device_codes[device_code.device_code] = device_code

            # Send response
            result = {
                "device_code": device_code.device_code,
                "user_code": device_code.user_code,
                "verification_uri": f"{self.config.server_url}/oauth/device/verify",
                "verification_uri_complete": f"{self.config.server_url}/oauth/device/verify?user_code={device_code.user_code}",
                "expires_in": self.config.device_code_lifetime,
                "interval": device_code.interval,
            }

            response = self._create_json_response(result)
            await send(response[0])
            await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"Device authorization endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in device authorization endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class JWKSEndpoint(BaseEndpoint):
    """OAuth2 JWKS endpoint for OpenID Connect."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle JWKS request."""
        try:
            # In a real implementation, this would return the server's public keys
            # For now, we'll return an empty JWKS
            result = {"keys": []}

            response = self._create_json_response(result)
            await send(response[0])
            await send(response[1])

        except Exception as e:
            self.logger.error(f"Unexpected error in JWKS endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])


class UserInfoEndpoint(BaseEndpoint):
    """OAuth2 user info endpoint for OpenID Connect."""

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle user info request."""
        try:
            # Get Authorization header
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("utf-8")

            if not auth_header.startswith("Bearer "):
                from .exceptions import InvalidTokenError

                raise InvalidTokenError("Invalid authorization header")

            token = auth_header[7:]  # Remove "Bearer " prefix

            # Get access token
            access_token = self.server.get_access_token(token)
            if not access_token or not access_token.is_valid():
                from .exceptions import InvalidTokenError

                raise InvalidTokenError("Invalid access token")

            # In a real implementation, this would return user information
            # For now, we'll return mock user info
            result = {
                "sub": access_token.user_id or "anonymous",
                "iss": self.config.issuer,
                "aud": access_token.client_id,
                "exp": int(access_token.expires_at.timestamp()),
                "iat": int(access_token.created_at.timestamp()),
                "scope": " ".join(access_token.scopes),
            }

            response = self._create_json_response(result)
            await send(response[0])
            await send(response[1])

        except OAuth2Error as e:
            self.logger.error(f"User info endpoint error: {e}")
            response = self._create_error_response(e)
            await send(response[0])
            await send(response[1])
        except Exception as e:
            self.logger.error(f"Unexpected error in user info endpoint: {e}")
            from .exceptions import ServerError

            error = ServerError("An unexpected error occurred")
            response = self._create_error_response(error, 500)
            await send(response[0])
            await send(response[1])
