"""
Tests for Keycloak exceptions.

Tests exception creation, error messages, and status codes.
"""

import pytest

from zephyr.security.keycloak.exceptions import (
    KeycloakError,
    KeycloakConnectionError,
    KeycloakAuthenticationError,
    KeycloakTokenError,
    KeycloakAdminError,
    KeycloakRealmNotFoundError,
    KeycloakUserNotFoundError,
    KeycloakInvalidTokenError,
    KeycloakExpiredTokenError,
)


class TestKeycloakExceptions:
    """Test Keycloak exception classes."""

    def test_base_error(self):
        """Test base Keycloak error."""
        error = KeycloakError("Test error", 500)

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code == 500

    def test_base_error_without_status_code(self):
        """Test base error without status code."""
        error = KeycloakError("Test error")

        assert str(error) == "Test error"
        assert error.status_code is None

    def test_connection_error(self):
        """Test connection error."""
        error = KeycloakConnectionError()

        assert "Failed to connect" in str(error)
        assert error.status_code is None

    def test_connection_error_custom_message(self):
        """Test connection error with custom message."""
        error = KeycloakConnectionError("Custom connection error")

        assert str(error) == "Custom connection error"

    def test_authentication_error(self):
        """Test authentication error."""
        error = KeycloakAuthenticationError()

        assert "Authentication failed" in str(error)

    def test_authentication_error_with_status_code(self):
        """Test authentication error with status code."""
        error = KeycloakAuthenticationError("Auth failed", 401)

        assert str(error) == "Auth failed"
        assert error.status_code == 401

    def test_token_error(self):
        """Test token error."""
        error = KeycloakTokenError()

        assert "Token operation failed" in str(error)

    def test_token_error_with_details(self):
        """Test token error with details."""
        error = KeycloakTokenError("Invalid token format", 400)

        assert str(error) == "Invalid token format"
        assert error.status_code == 400

    def test_admin_error(self):
        """Test admin API error."""
        error = KeycloakAdminError()

        assert "Admin API operation failed" in str(error)

    def test_admin_error_with_details(self):
        """Test admin error with details."""
        error = KeycloakAdminError("User creation failed", 403)

        assert str(error) == "User creation failed"
        assert error.status_code == 403

    def test_realm_not_found_error(self):
        """Test realm not found error."""
        error = KeycloakRealmNotFoundError("test-realm")

        assert "test-realm" in str(error)
        assert error.realm == "test-realm"
        assert error.status_code == 404

    def test_user_not_found_error(self):
        """Test user not found error."""
        error = KeycloakUserNotFoundError("user-123")

        assert "user-123" in str(error)
        assert error.user_id == "user-123"
        assert error.status_code == 404

    def test_invalid_token_error(self):
        """Test invalid token error."""
        error = KeycloakInvalidTokenError()

        assert "Invalid token" in str(error)
        assert error.status_code == 401

    def test_invalid_token_error_custom_message(self):
        """Test invalid token error with custom message."""
        error = KeycloakInvalidTokenError("Token signature invalid")

        assert str(error) == "Token signature invalid"
        assert error.status_code == 401

    def test_expired_token_error(self):
        """Test expired token error."""
        error = KeycloakExpiredTokenError()

        assert "Token expired" in str(error)
        assert error.status_code == 401

    def test_expired_token_error_custom_message(self):
        """Test expired token error with custom message."""
        error = KeycloakExpiredTokenError("Access token has expired")

        assert str(error) == "Access token has expired"
        assert error.status_code == 401

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        assert issubclass(KeycloakConnectionError, KeycloakError)
        assert issubclass(KeycloakAuthenticationError, KeycloakError)
        assert issubclass(KeycloakTokenError, KeycloakError)
        assert issubclass(KeycloakAdminError, KeycloakError)
        assert issubclass(KeycloakRealmNotFoundError, KeycloakError)
        assert issubclass(KeycloakUserNotFoundError, KeycloakError)
        assert issubclass(KeycloakInvalidTokenError, KeycloakTokenError)
        assert issubclass(KeycloakExpiredTokenError, KeycloakTokenError)

    def test_exception_can_be_raised(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(KeycloakError):
            raise KeycloakError("Test error")

        with pytest.raises(KeycloakConnectionError):
            raise KeycloakConnectionError()

        with pytest.raises(KeycloakAuthenticationError):
            raise KeycloakAuthenticationError()

    def test_catch_base_exception(self):
        """Test catching specific exceptions with base exception."""
        try:
            raise KeycloakAuthenticationError("Auth failed")
        except KeycloakError as e:
            assert isinstance(e, KeycloakAuthenticationError)
            assert str(e) == "Auth failed"
