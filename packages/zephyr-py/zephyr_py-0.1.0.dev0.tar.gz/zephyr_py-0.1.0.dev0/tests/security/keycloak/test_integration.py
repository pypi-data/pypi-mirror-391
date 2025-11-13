"""
Tests for Keycloak integration scenarios.

End-to-end integration tests for complete authentication flows.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from zephyr.security.keycloak.client import KeycloakClient
from zephyr.security.keycloak.admin import KeycloakAdmin
from zephyr.security.keycloak.provider import KeycloakSSOProvider
from zephyr.security.keycloak.models import KeycloakUser


class TestKeycloakIntegration:
    """Test Keycloak integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_authentication_flow(self, keycloak_config, mock_token_response, mock_userinfo_response):
        """Test complete authentication flow from authorization to user info."""
        async with KeycloakClient(keycloak_config) as client:
            # Step 1: Get authorization URL
            auth_url = client.get_authorization_url(redirect_uri="https://example.com/callback", state="test-state")

            assert "https://keycloak.example.com" in auth_url
            assert "client_id=test-client" in auth_url

            # Step 2: Exchange code for token (mocked)
            with patch.object(client.http_client, "post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_token_response
                mock_post.return_value = mock_response

                token = await client.exchange_code_for_token(
                    code="auth_code", redirect_uri="https://example.com/callback"
                )

                assert token.access_token is not None

            # Step 3: Get user info (mocked)
            with patch.object(client.http_client, "get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_userinfo_response
                mock_get.return_value = mock_response

                user_info = await client.get_user_info(token.access_token)

                assert user_info.sub == "user-123"
                assert user_info.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, keycloak_config, mock_token_response):
        """Test token refresh flow."""
        async with KeycloakClient(keycloak_config) as client:
            with patch.object(client.http_client, "post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_token_response
                mock_post.return_value = mock_response

                # Get initial token
                token = await client.exchange_code_for_token(
                    code="auth_code", redirect_uri="https://example.com/callback"
                )

                # Refresh token
                new_token = await client.refresh_token(token.refresh_token)

                assert new_token.access_token is not None

    @pytest.mark.asyncio
    async def test_sso_provider_full_flow(self, keycloak_config, sample_token, sample_user_info):
        """Test SSO provider complete authentication flow."""
        provider = KeycloakSSOProvider(keycloak_config)
        provider.config["redirect_uri"] = "https://example.com/callback"

        with (
            patch.object(provider.keycloak_client, "exchange_code_for_token") as mock_exchange,
            patch.object(provider.keycloak_client, "get_user_info") as mock_get_user,
        ):
            mock_exchange.return_value = sample_token
            mock_get_user.return_value = sample_user_info

            # Complete authentication
            result = await provider.authenticate("auth_code", "test-state")

            assert result.success is True
            assert result.user.email == "test@example.com"

            # Validate token
            with patch.object(provider.keycloak_client, "validate_token") as mock_validate:
                mock_validate.return_value = {"sub": "user-123", "exp": 9999999999}

                claims = await provider.validate_token(sample_token.access_token)

                assert claims["sub"] == "user-123"

    @pytest.mark.asyncio
    async def test_admin_user_management_flow(self, keycloak_config):
        """Test admin API user management flow."""
        async with KeycloakAdmin(keycloak_config) as admin:
            with patch.object(admin, "_request") as mock_request:
                # Create user
                create_response = Mock()
                create_response.status_code = 201
                create_response.headers = {
                    "Location": "https://keycloak.example.com/admin/realms/test-realm/users/new-user-123"
                }
                mock_request.return_value = create_response

                new_user = KeycloakUser(
                    username="newuser", email="newuser@example.com", first_name="New", last_name="User", enabled=True
                )

                user_id = await admin.create_user(new_user)

                assert user_id == "new-user-123"

                # Get user
                get_response = Mock()
                get_response.status_code = 200
                get_response.json.return_value = new_user.dict()
                mock_request.return_value = get_response

                retrieved_user = await admin.get_user(user_id)

                assert retrieved_user.username == "newuser"

                # Update user
                update_response = Mock()
                update_response.status_code = 204
                mock_request.return_value = update_response

                new_user.first_name = "Updated"
                await admin.update_user(user_id, new_user)

                # Delete user
                delete_response = Mock()
                delete_response.status_code = 204
                mock_request.return_value = delete_response

                await admin.delete_user(user_id)

    @pytest.mark.asyncio
    async def test_pkce_flow(self, keycloak_config, mock_token_response):
        """Test PKCE authentication flow."""
        async with KeycloakClient(keycloak_config) as client:
            # Generate PKCE challenge
            code_verifier, code_challenge = client.generate_pkce_challenge()

            assert code_verifier is not None
            assert code_challenge is not None

            # Get authorization URL with PKCE
            auth_url = client.get_authorization_url(
                redirect_uri="https://example.com/callback",
                state="test-state",
                code_challenge=code_challenge,
                code_challenge_method="S256",
            )

            assert "code_challenge" in auth_url

            # Exchange code with PKCE verifier
            with patch.object(client.http_client, "post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_token_response
                mock_post.return_value = mock_response

                token = await client.exchange_code_for_token(
                    code="auth_code", redirect_uri="https://example.com/callback", code_verifier=code_verifier
                )

                assert token.access_token is not None

    @pytest.mark.asyncio
    async def test_logout_flow(self, keycloak_config, sample_token):
        """Test complete logout flow."""
        async with KeycloakClient(keycloak_config) as client:
            with patch.object(client.http_client, "post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 204
                mock_post.return_value = mock_response

                # Logout
                await client.logout(refresh_token=sample_token.refresh_token, redirect_uri="https://example.com")

                # Verify logout was called
                assert mock_post.called

    @pytest.mark.asyncio
    async def test_role_assignment_flow(self, keycloak_config, sample_role):
        """Test role assignment flow."""
        async with KeycloakAdmin(keycloak_config) as admin:
            with patch.object(admin, "_request") as mock_request:
                # Get realm roles
                roles_response = Mock()
                roles_response.status_code = 200
                roles_response.json.return_value = [sample_role.dict()]
                mock_request.return_value = roles_response

                roles = await admin.get_realm_roles()

                assert len(roles) == 1

                # Assign role to user
                assign_response = Mock()
                assign_response.status_code = 204
                mock_request.return_value = assign_response

                await admin.assign_realm_roles("user-123", roles)

                # Get user roles
                user_roles_response = Mock()
                user_roles_response.status_code = 200
                user_roles_response.json.return_value = [sample_role.dict()]
                mock_request.return_value = user_roles_response

                user_roles = await admin.get_user_realm_roles("user-123")

                assert len(user_roles) == 1
                assert user_roles[0].name == sample_role.name

    @pytest.mark.asyncio
    async def test_group_membership_flow(self, keycloak_config, sample_group):
        """Test group membership flow."""
        async with KeycloakAdmin(keycloak_config) as admin:
            with patch.object(admin, "_request") as mock_request:
                # Get groups
                groups_response = Mock()
                groups_response.status_code = 200
                groups_response.json.return_value = [sample_group.dict()]
                mock_request.return_value = groups_response

                groups = await admin.get_groups()

                assert len(groups) == 1

                # Add user to group
                add_response = Mock()
                add_response.status_code = 204
                mock_request.return_value = add_response

                await admin.add_user_to_group("user-123", sample_group.id)

                # Get user groups
                user_groups_response = Mock()
                user_groups_response.status_code = 200
                user_groups_response.json.return_value = [sample_group.dict()]
                mock_request.return_value = user_groups_response

                user_groups = await admin.get_user_groups("user-123")

                assert len(user_groups) == 1
                assert user_groups[0].name == sample_group.name
