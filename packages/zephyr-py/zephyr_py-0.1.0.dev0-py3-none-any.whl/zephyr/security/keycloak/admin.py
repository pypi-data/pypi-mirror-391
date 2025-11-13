"""
Keycloak Admin API client implementation.

Provides admin operations for user, role, group, and client management.
"""

from typing import Any

import httpx

from .config import KeycloakConfig
from .exceptions import (
    KeycloakAdminError,
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakUserNotFoundError,
)
from .models import KeycloakClient, KeycloakGroup, KeycloakRole, KeycloakUser


class KeycloakAdmin:
    """Keycloak Admin API client."""

    def __init__(self, config: KeycloakConfig) -> None:
        """
        Initialize Keycloak admin client.

        Args:
            config: Keycloak configuration
        """
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=config.timeout, verify=config.verify_ssl)
        self._admin_token: str | None = None

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self) -> "KeycloakAdmin":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def get_admin_token(self) -> str:
        """
        Get admin access token.

        Returns:
            Admin access token

        Raises:
            KeycloakAuthenticationError: If authentication fails
            KeycloakConnectionError: If connection fails
        """
        if not self.config.admin_username or not self.config.admin_password:
            raise KeycloakAuthenticationError("Admin credentials not configured")

        data = {
            "grant_type": "password",
            "client_id": self.config.admin_client_id,
            "username": self.config.admin_username,
            "password": self.config.admin_password,
        }

        try:
            response = await self.http_client.post(
                self.config.get_admin_token_endpoint(),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                raise KeycloakAuthenticationError(f"Admin authentication failed: {response.text}", response.status_code)

            token_data = response.json()
            self._admin_token = token_data["access_token"]
            return self._admin_token

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """
        Make authenticated admin API request.

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            KeycloakAdminError: If request fails
            KeycloakConnectionError: If connection fails
        """
        if not self._admin_token:
            await self.get_admin_token()

        url = f"{self.config.get_admin_url()}{path}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._admin_token}"

        try:
            response = await self.http_client.request(method, url, headers=headers, **kwargs)

            # Retry with new token if unauthorized
            if response.status_code == 401:
                await self.get_admin_token()
                headers["Authorization"] = f"Bearer {self._admin_token}"
                response = await self.http_client.request(method, url, headers=headers, **kwargs)

            return response

        except httpx.RequestError as e:
            raise KeycloakConnectionError(f"Connection failed: {str(e)}")

    # User Management

    async def create_user(self, user: KeycloakUser) -> str:
        """
        Create a new user.

        Args:
            user: User data

        Returns:
            Created user ID

        Raises:
            KeycloakAdminError: If user creation fails
        """
        response = await self._request("POST", "/users", json=user.dict(exclude_none=True, exclude={"id"}))

        if response.status_code != 201:
            raise KeycloakAdminError(f"Failed to create user: {response.text}", response.status_code)

        # Extract user ID from Location header
        location = response.headers.get("Location", "")
        user_id = location.split("/")[-1]
        return user_id

    async def get_user(self, user_id: str) -> KeycloakUser:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User data

        Raises:
            KeycloakUserNotFoundError: If user not found
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", f"/users/{user_id}")

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(user_id)

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get user: {response.text}", response.status_code)

        return KeycloakUser(**response.json())

    async def get_user_by_username(self, username: str) -> KeycloakUser | None:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User data or None if not found

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", "/users", params={"username": username, "exact": "true"})

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to search users: {response.text}", response.status_code)

        users = response.json()
        if not users:
            return None

        return KeycloakUser(**users[0])

    async def update_user(self, user_id: str, user: KeycloakUser) -> None:
        """
        Update user.

        Args:
            user_id: User ID
            user: Updated user data

        Raises:
            KeycloakUserNotFoundError: If user not found
            KeycloakAdminError: If update fails
        """
        response = await self._request("PUT", f"/users/{user_id}", json=user.dict(exclude_none=True, exclude={"id"}))

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(user_id)

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to update user: {response.text}", response.status_code)

    async def delete_user(self, user_id: str) -> None:
        """
        Delete user.

        Args:
            user_id: User ID

        Raises:
            KeycloakUserNotFoundError: If user not found
            KeycloakAdminError: If deletion fails
        """
        response = await self._request("DELETE", f"/users/{user_id}")

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(user_id)

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to delete user: {response.text}", response.status_code)

    async def list_users(self, first: int = 0, max_results: int = 100, search: str | None = None) -> list[KeycloakUser]:
        """
        List users.

        Args:
            first: First result index
            max_results: Maximum number of results
            search: Search query

        Returns:
            List of users

        Raises:
            KeycloakAdminError: If request fails
        """
        params: dict[str, Any] = {"first": first, "max": max_results}
        if search:
            params["search"] = search

        response = await self._request("GET", "/users", params=params)

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to list users: {response.text}", response.status_code)

        return [KeycloakUser(**user) for user in response.json()]

    async def reset_user_password(self, user_id: str, password: str, temporary: bool = False) -> None:
        """
        Reset user password.

        Args:
            user_id: User ID
            password: New password
            temporary: Whether password is temporary

        Raises:
            KeycloakUserNotFoundError: If user not found
            KeycloakAdminError: If reset fails
        """
        credential = {"type": "password", "value": password, "temporary": temporary}

        response = await self._request("PUT", f"/users/{user_id}/reset-password", json=credential)

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(user_id)

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to reset password: {response.text}", response.status_code)

    # Role Management

    async def get_realm_roles(self) -> list[KeycloakRole]:
        """
        Get all realm roles.

        Returns:
            List of realm roles

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", "/roles")

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get realm roles: {response.text}", response.status_code)

        return [KeycloakRole(**role) for role in response.json()]

    async def get_user_realm_roles(self, user_id: str) -> list[KeycloakRole]:
        """
        Get user's realm roles.

        Args:
            user_id: User ID

        Returns:
            List of user's realm roles

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", f"/users/{user_id}/role-mappings/realm")

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get user roles: {response.text}", response.status_code)

        return [KeycloakRole(**role) for role in response.json()]

    async def assign_realm_roles(self, user_id: str, roles: list[KeycloakRole]) -> None:
        """
        Assign realm roles to user.

        Args:
            user_id: User ID
            roles: Roles to assign

        Raises:
            KeycloakAdminError: If assignment fails
        """
        role_data = [role.dict(include={"id", "name"}) for role in roles]

        response = await self._request("POST", f"/users/{user_id}/role-mappings/realm", json=role_data)

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to assign roles: {response.text}", response.status_code)

    async def remove_realm_roles(self, user_id: str, roles: list[KeycloakRole]) -> None:
        """
        Remove realm roles from user.

        Args:
            user_id: User ID
            roles: Roles to remove

        Raises:
            KeycloakAdminError: If removal fails
        """
        role_data = [role.dict(include={"id", "name"}) for role in roles]

        response = await self._request("DELETE", f"/users/{user_id}/role-mappings/realm", json=role_data)

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to remove roles: {response.text}", response.status_code)

    # Group Management

    async def get_groups(self) -> list[KeycloakGroup]:
        """
        Get all groups.

        Returns:
            List of groups

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", "/groups")

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get groups: {response.text}", response.status_code)

        return [KeycloakGroup(**group) for group in response.json()]

    async def get_user_groups(self, user_id: str) -> list[KeycloakGroup]:
        """
        Get user's groups.

        Args:
            user_id: User ID

        Returns:
            List of user's groups

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", f"/users/{user_id}/groups")

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get user groups: {response.text}", response.status_code)

        return [KeycloakGroup(**group) for group in response.json()]

    async def add_user_to_group(self, user_id: str, group_id: str) -> None:
        """
        Add user to group.

        Args:
            user_id: User ID
            group_id: Group ID

        Raises:
            KeycloakAdminError: If operation fails
        """
        response = await self._request("PUT", f"/users/{user_id}/groups/{group_id}")

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to add user to group: {response.text}", response.status_code)

    async def remove_user_from_group(self, user_id: str, group_id: str) -> None:
        """
        Remove user from group.

        Args:
            user_id: User ID
            group_id: Group ID

        Raises:
            KeycloakAdminError: If operation fails
        """
        response = await self._request("DELETE", f"/users/{user_id}/groups/{group_id}")

        if response.status_code != 204:
            raise KeycloakAdminError(f"Failed to remove user from group: {response.text}", response.status_code)

    # Client Management

    async def get_clients(self) -> list[KeycloakClient]:
        """
        Get all clients.

        Returns:
            List of clients

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", "/clients")

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get clients: {response.text}", response.status_code)

        return [KeycloakClient(**client) for client in response.json()]

    async def get_client_by_client_id(self, client_id: str) -> KeycloakClient | None:
        """
        Get client by client ID.

        Args:
            client_id: Client identifier

        Returns:
            Client data or None if not found

        Raises:
            KeycloakAdminError: If request fails
        """
        response = await self._request("GET", "/clients", params={"clientId": client_id})

        if response.status_code != 200:
            raise KeycloakAdminError(f"Failed to get client: {response.text}", response.status_code)

        clients = response.json()
        if not clients:
            return None

        return KeycloakClient(**clients[0])
