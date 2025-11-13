"""
Tests for Keycloak Admin API client.

Tests user, role, group, and client management operations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from zephyr.security.keycloak.admin import KeycloakAdmin
from zephyr.security.keycloak.exceptions import (
    KeycloakAdminError,
    KeycloakAuthenticationError,
    KeycloakUserNotFoundError,
)
from zephyr.security.keycloak.models import KeycloakUser, KeycloakRole, KeycloakGroup


class TestKeycloakAdmin:
    """Test Keycloak Admin API client."""

    @pytest.mark.asyncio
    async def test_admin_initialization(self, keycloak_config):
        """Test admin client initialization."""
        async with KeycloakAdmin(keycloak_config) as admin:
            assert admin.config == keycloak_config
            assert admin.http_client is not None

    @pytest.mark.asyncio
    async def test_get_admin_token_success(self, keycloak_config):
        """Test successful admin token retrieval."""
        token_response = {"access_token": "admin_token"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = token_response

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                token = await admin.get_admin_token()

                assert token == "admin_token"
                assert admin._admin_token == "admin_token"

    @pytest.mark.asyncio
    async def test_get_admin_token_no_credentials(self):
        """Test admin token retrieval without credentials."""
        from zephyr.security.keycloak.config import KeycloakConfig

        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
        )

        async with KeycloakAdmin(config) as admin:
            with pytest.raises(KeycloakAuthenticationError):
                await admin.get_admin_token()

    @pytest.mark.asyncio
    async def test_create_user_success(self, keycloak_config, sample_user):
        """Test successful user creation."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Mock admin token response
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            # Mock create user response
            create_response = Mock(spec=httpx.Response)
            create_response.status_code = 201
            create_response.headers = {
                "Location": "https://keycloak.example.com/admin/realms/test-realm/users/user-123"
            }
            create_response.text = ""

            mock_client = AsyncMock()
            mock_client.post.side_effect = [token_response, create_response]
            mock_client.request.return_value = create_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                user_id = await admin.create_user(sample_user)

                assert user_id == "user-123"

    @pytest.mark.asyncio
    async def test_get_user_success(self, keycloak_config, sample_user):
        """Test successful user retrieval."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Mock admin token
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            # Mock get user response
            user_response = Mock(spec=httpx.Response)
            user_response.status_code = 200
            user_response.json.return_value = sample_user.dict()

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = user_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                user = await admin.get_user("user-123")

                assert user.id == "user-123"
                assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, keycloak_config):
        """Test user not found."""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Mock admin token
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            # Mock not found response
            not_found_response = Mock(spec=httpx.Response)
            not_found_response.status_code = 404

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = not_found_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                with pytest.raises(KeycloakUserNotFoundError):
                    await admin.get_user("nonexistent")

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, keycloak_config, sample_user):
        """Test user retrieval by username."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            user_response = Mock(spec=httpx.Response)
            user_response.status_code = 200
            user_response.json.return_value = [sample_user.dict()]

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = user_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                user = await admin.get_user_by_username("testuser")

                assert user is not None
                assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_update_user_success(self, keycloak_config, sample_user):
        """Test successful user update."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            update_response = Mock(spec=httpx.Response)
            update_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = update_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                await admin.update_user("user-123", sample_user)

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_delete_user_success(self, keycloak_config):
        """Test successful user deletion."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            delete_response = Mock(spec=httpx.Response)
            delete_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = delete_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                await admin.delete_user("user-123")

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_list_users(self, keycloak_config, sample_user):
        """Test listing users."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            list_response = Mock(spec=httpx.Response)
            list_response.status_code = 200
            list_response.json.return_value = [sample_user.dict()]

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = list_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                users = await admin.list_users()

                assert len(users) == 1
                assert users[0].username == "testuser"

    @pytest.mark.asyncio
    async def test_reset_password(self, keycloak_config):
        """Test password reset."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            reset_response = Mock(spec=httpx.Response)
            reset_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = reset_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                await admin.reset_user_password("user-123", "newpassword", temporary=True)

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_get_realm_roles(self, keycloak_config, sample_role):
        """Test getting realm roles."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            roles_response = Mock(spec=httpx.Response)
            roles_response.status_code = 200
            roles_response.json.return_value = [sample_role.dict()]

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = roles_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                roles = await admin.get_realm_roles()

                assert len(roles) == 1
                assert roles[0].name == "test-role"

    @pytest.mark.asyncio
    async def test_assign_realm_roles(self, keycloak_config, sample_role):
        """Test assigning realm roles to user."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            assign_response = Mock(spec=httpx.Response)
            assign_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = assign_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                await admin.assign_realm_roles("user-123", [sample_role])

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_get_groups(self, keycloak_config, sample_group):
        """Test getting groups."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            groups_response = Mock(spec=httpx.Response)
            groups_response.status_code = 200
            groups_response.json.return_value = [sample_group.dict()]

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = groups_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                groups = await admin.get_groups()

                assert len(groups) == 1
                assert groups[0].name == "test-group"

    @pytest.mark.asyncio
    async def test_add_user_to_group(self, keycloak_config):
        """Test adding user to group."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            add_response = Mock(spec=httpx.Response)
            add_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = add_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                await admin.add_user_to_group("user-123", "group-123")

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_get_clients(self, keycloak_config, sample_client):
        """Test getting clients."""
        with patch("httpx.AsyncClient") as mock_client_class:
            token_response = Mock(spec=httpx.Response)
            token_response.status_code = 200
            token_response.json.return_value = {"access_token": "admin_token"}

            clients_response = Mock(spec=httpx.Response)
            clients_response.status_code = 200
            clients_response.json.return_value = [sample_client.dict()]

            mock_client = AsyncMock()
            mock_client.post.return_value = token_response
            mock_client.request.return_value = clients_response
            mock_client_class.return_value = mock_client

            async with KeycloakAdmin(keycloak_config) as admin:
                admin.http_client = mock_client

                clients = await admin.get_clients()

                assert len(clients) == 1
                assert clients[0].client_id == "test-client"
