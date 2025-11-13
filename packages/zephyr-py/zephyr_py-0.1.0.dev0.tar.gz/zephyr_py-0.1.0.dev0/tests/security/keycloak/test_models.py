"""
Tests for Keycloak data models.

Tests model creation, validation, and helper methods.
"""

import pytest
from datetime import datetime, timedelta

from zephyr.security.keycloak.models import (
    KeycloakToken,
    KeycloakUser,
    KeycloakUserInfo,
    KeycloakRole,
    KeycloakGroup,
    KeycloakClient,
    KeycloakRealm,
)


class TestKeycloakToken:
    """Test Keycloak token model."""

    def test_token_creation(self, sample_token):
        """Test token creation."""
        assert sample_token.access_token == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
        assert sample_token.token_type == "Bearer"
        assert sample_token.expires_in == 300
        assert sample_token.refresh_token == "refresh_token_value"
        assert sample_token.refresh_expires_in == 1800

    def test_token_expiry_check(self):
        """Test token expiry checking."""
        token = KeycloakToken(
            access_token="test_token", expires_in=300, issued_at=datetime.utcnow() - timedelta(seconds=400)
        )

        assert token.is_expired() is True

    def test_token_not_expired(self):
        """Test token not expired."""
        token = KeycloakToken(access_token="test_token", expires_in=300, issued_at=datetime.utcnow())

        assert token.is_expired() is False

    def test_refresh_token_expiry(self):
        """Test refresh token expiry checking."""
        token = KeycloakToken(
            access_token="test_token",
            expires_in=300,
            refresh_token="refresh_token",
            refresh_expires_in=1800,
            issued_at=datetime.utcnow() - timedelta(seconds=2000),
        )

        assert token.is_refresh_expired() is True

    def test_refresh_token_not_expired(self):
        """Test refresh token not expired."""
        token = KeycloakToken(
            access_token="test_token",
            expires_in=300,
            refresh_token="refresh_token",
            refresh_expires_in=1800,
            issued_at=datetime.utcnow(),
        )

        assert token.is_refresh_expired() is False


class TestKeycloakUser:
    """Test Keycloak user model."""

    def test_user_creation(self, sample_user):
        """Test user creation."""
        assert sample_user.id == "user-123"
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"
        assert sample_user.email_verified is True
        assert sample_user.first_name == "Test"
        assert sample_user.last_name == "User"
        assert sample_user.enabled is True

    def test_get_full_name(self, sample_user):
        """Test getting user's full name."""
        assert sample_user.get_full_name() == "Test User"

    def test_get_full_name_first_only(self):
        """Test getting full name with only first name."""
        user = KeycloakUser(username="testuser", first_name="Test")

        assert user.get_full_name() == "Test"

    def test_get_full_name_username_fallback(self):
        """Test full name falls back to username."""
        user = KeycloakUser(username="testuser")

        assert user.get_full_name() == "testuser"

    def test_has_role(self, sample_user):
        """Test checking if user has role."""
        assert sample_user.has_role("user") is True
        assert sample_user.has_role("admin") is True
        assert sample_user.has_role("superadmin") is False

    def test_has_client_role(self):
        """Test checking if user has client role."""
        user = KeycloakUser(username="testuser", client_roles={"test-client": ["admin", "user"]})

        assert user.has_client_role("test-client", "admin") is True
        assert user.has_client_role("test-client", "user") is True
        assert user.has_client_role("test-client", "superadmin") is False
        assert user.has_client_role("other-client", "admin") is False


class TestKeycloakUserInfo:
    """Test Keycloak UserInfo model."""

    def test_userinfo_creation(self, sample_user_info):
        """Test UserInfo creation."""
        assert sample_user_info.sub == "user-123"
        assert sample_user_info.email == "test@example.com"
        assert sample_user_info.email_verified is True
        assert sample_user_info.preferred_username == "testuser"
        assert sample_user_info.given_name == "Test"
        assert sample_user_info.family_name == "User"
        assert sample_user_info.name == "Test User"

    def test_userinfo_extra_fields(self):
        """Test UserInfo with extra fields."""
        userinfo = KeycloakUserInfo(sub="user-123", email="test@example.com", custom_field="custom_value")

        assert userinfo.sub == "user-123"
        # Extra fields should be allowed
        assert hasattr(userinfo, "custom_field")


class TestKeycloakRole:
    """Test Keycloak role model."""

    def test_role_creation(self, sample_role):
        """Test role creation."""
        assert sample_role.id == "role-123"
        assert sample_role.name == "test-role"
        assert sample_role.description == "Test role"
        assert sample_role.composite is False
        assert sample_role.client_role is False

    def test_composite_role(self):
        """Test composite role."""
        role = KeycloakRole(name="composite-role", composite=True, composites={"realm": ["user", "admin"]})

        assert role.composite is True
        assert "realm" in role.composites


class TestKeycloakGroup:
    """Test Keycloak group model."""

    def test_group_creation(self, sample_group):
        """Test group creation."""
        assert sample_group.id == "group-123"
        assert sample_group.name == "test-group"
        assert sample_group.path == "/test-group"
        assert "user" in sample_group.realm_roles

    def test_group_with_subgroups(self):
        """Test group with subgroups."""
        subgroup = KeycloakGroup(id="subgroup-123", name="subgroup", path="/test-group/subgroup")

        group = KeycloakGroup(name="test-group", path="/test-group", sub_groups=[subgroup])

        assert len(group.sub_groups) == 1
        assert group.sub_groups[0].name == "subgroup"


class TestKeycloakClient:
    """Test Keycloak client model."""

    def test_client_creation(self, sample_client):
        """Test client creation."""
        assert sample_client.id == "client-uuid-123"
        assert sample_client.client_id == "test-client"
        assert sample_client.name == "Test Client"
        assert sample_client.enabled is True
        assert sample_client.public_client is False

    def test_public_client(self):
        """Test public client."""
        client = KeycloakClient(client_id="public-client", public_client=True)

        assert client.public_client is True

    def test_client_redirect_uris(self, sample_client):
        """Test client redirect URIs."""
        assert len(sample_client.redirect_uris) == 1
        assert sample_client.redirect_uris[0] == "https://example.com/callback"


class TestKeycloakRealm:
    """Test Keycloak realm model."""

    def test_realm_creation(self):
        """Test realm creation."""
        realm = KeycloakRealm(realm="test-realm", display_name="Test Realm", enabled=True)

        assert realm.realm == "test-realm"
        assert realm.display_name == "Test Realm"
        assert realm.enabled is True

    def test_realm_token_settings(self):
        """Test realm token settings."""
        realm = KeycloakRealm(realm="test-realm", access_token_lifespan=600, refresh_token_lifespan=3600)

        assert realm.access_token_lifespan == 600
        assert realm.refresh_token_lifespan == 3600

    def test_realm_ssl_settings(self):
        """Test realm SSL settings."""
        realm = KeycloakRealm(realm="test-realm", ssl_required="all")

        assert realm.ssl_required == "all"
