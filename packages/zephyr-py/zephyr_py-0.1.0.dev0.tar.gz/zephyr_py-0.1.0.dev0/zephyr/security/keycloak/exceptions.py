"""
Keycloak exception classes.

Defines custom exceptions for Keycloak integration errors.
"""

from zephyr.exceptions import BaseZephyrException


class KeycloakError(BaseZephyrException):
    """Base exception for Keycloak errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """
        Initialize Keycloak error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class KeycloakConnectionError(KeycloakError):
    """Exception raised when connection to Keycloak server fails."""

    def __init__(self, message: str = "Failed to connect to Keycloak server") -> None:
        """Initialize connection error."""
        super().__init__(message)


class KeycloakAuthenticationError(KeycloakError):
    """Exception raised when authentication with Keycloak fails."""

    def __init__(self, message: str = "Authentication failed", status_code: int | None = None) -> None:
        """Initialize authentication error."""
        super().__init__(message, status_code)


class KeycloakTokenError(KeycloakError):
    """Exception raised when token operations fail."""

    def __init__(self, message: str = "Token operation failed", status_code: int | None = None) -> None:
        """Initialize token error."""
        super().__init__(message, status_code)


class KeycloakAdminError(KeycloakError):
    """Exception raised when admin API operations fail."""

    def __init__(self, message: str = "Admin API operation failed", status_code: int | None = None) -> None:
        """Initialize admin error."""
        super().__init__(message, status_code)


class KeycloakRealmNotFoundError(KeycloakError):
    """Exception raised when realm is not found."""

    def __init__(self, realm: str) -> None:
        """Initialize realm not found error."""
        super().__init__(f"Realm '{realm}' not found", 404)
        self.realm = realm


class KeycloakUserNotFoundError(KeycloakError):
    """Exception raised when user is not found."""

    def __init__(self, user_id: str) -> None:
        """Initialize user not found error."""
        super().__init__(f"User '{user_id}' not found", 404)
        self.user_id = user_id


class KeycloakInvalidTokenError(KeycloakTokenError):
    """Exception raised when token is invalid."""

    def __init__(self, message: str = "Invalid token") -> None:
        """Initialize invalid token error."""
        super().__init__(message, 401)


class KeycloakExpiredTokenError(KeycloakTokenError):
    """Exception raised when token is expired."""

    def __init__(self, message: str = "Token expired") -> None:
        """Initialize expired token error."""
        super().__init__(message, 401)
