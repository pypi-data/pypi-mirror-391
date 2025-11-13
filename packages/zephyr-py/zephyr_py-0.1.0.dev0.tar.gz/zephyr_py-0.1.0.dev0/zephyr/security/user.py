"""
User models for Zephyr authentication.

Provides User and AnonymousUser classes with role and permission management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class User:
    """
    Authenticated user model.

    Represents an authenticated user with roles, permissions, and authentication state.
    """

    def __init__(
        self,
        id: str,
        username: str,
        email: str,
        is_active: bool = True,
        is_superuser: bool = False,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        mfa_enabled: bool = False,
    ) -> None:
        """
        Initialize user.

        Args:
            id: Unique user identifier
            username: Username
            email: Email address
            is_active: Whether user account is active
            is_superuser: Whether user is a superuser
            roles: List of user roles
            permissions: List of user permissions
            mfa_enabled: Whether MFA is enabled for user
        """
        self.id = id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.roles = roles or []
        self.permissions = permissions or []
        self.mfa_enabled = mfa_enabled

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        return False

    async def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise
        """
        if not permission:
            return False

        # Superusers have all permissions
        if self.is_superuser:
            return True

        # Check direct permissions
        if permission in self.permissions:
            return True

        # Check role-based permissions (simplified)
        # In a real implementation, you would check role permissions
        return False

    async def has_role(self, role: str) -> bool:
        """
        Check if user has specific role.

        Args:
            role: Role to check

        Returns:
            True if user has role, False otherwise
        """
        if not role:
            return False

        return role in self.roles

    async def has_any_role(self, roles: list[str]) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            roles: List of roles to check

        Returns:
            True if user has any of the roles, False otherwise
        """
        if not roles:
            return False

        return any([await self.has_role(role) for role in roles])

    async def has_all_roles(self, roles: list[str]) -> bool:
        """
        Check if user has all of the specified roles.

        Args:
            roles: List of roles to check

        Returns:
            True if user has all roles, False otherwise
        """
        if not roles:
            return True

        return all([await self.has_role(role) for role in roles])

    async def has_any_permission(self, permissions: list[str]) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            permissions: List of permissions to check

        Returns:
            True if user has any of the permissions, False otherwise
        """
        if not permissions:
            return False

        return any([await self.has_permission(permission) for permission in permissions])

    async def has_all_permissions(self, permissions: list[str]) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            permissions: List of permissions to check

        Returns:
            True if user has all permissions, False otherwise
        """
        if not permissions:
            return True

        return all([await self.has_permission(permission) for permission in permissions])

    def to_dict(self) -> dict[str, object]:
        """
        Convert user to dictionary.

        Returns:
            User data as dictionary
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "roles": self.roles,
            "permissions": self.permissions,
            "mfa_enabled": self.mfa_enabled,
            "is_authenticated": self.is_authenticated,
            "is_anonymous": self.is_anonymous,
        }

    def __str__(self) -> str:
        """String representation of user."""
        return f"User(id={self.id}, username={self.username}, email={self.email})"

    def __repr__(self) -> str:
        """Detailed string representation of user."""
        return (
            f"User(id={self.id}, username={self.username}, email={self.email}, "
            f"is_active={self.is_active}, is_superuser={self.is_superuser}, "
            f"roles={self.roles}, permissions={self.permissions}, "
            f"mfa_enabled={self.mfa_enabled})"
        )


class AnonymousUser:
    """
    Anonymous (unauthenticated) user model.

    Represents an unauthenticated user with no permissions or roles.
    """

    def __init__(self) -> None:
        """Initialize anonymous user."""
        self.id = None
        self.username = None
        self.email = None
        self.is_active = False
        self.is_superuser = False
        self.roles = []
        self.permissions = []
        self.mfa_enabled = False

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return False

    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        return True

    async def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.

        Args:
            permission: Permission to check

        Returns:
            Always False for anonymous users
        """
        return False

    async def has_role(self, role: str) -> bool:
        """
        Check if user has specific role.

        Args:
            role: Role to check

        Returns:
            Always False for anonymous users
        """
        return False

    async def has_any_role(self, roles: list[str]) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            roles: List of roles to check

        Returns:
            Always False for anonymous users
        """
        return False

    async def has_all_roles(self, roles: list[str]) -> bool:
        """
        Check if user has all of the specified roles.

        Args:
            roles: List of roles to check

        Returns:
            Always False for anonymous users
        """
        return False

    async def has_any_permission(self, permissions: list[str]) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            permissions: List of permissions to check

        Returns:
            Always False for anonymous users
        """
        return False

    async def has_all_permissions(self, permissions: list[str]) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            permissions: List of permissions to check

        Returns:
            Always False for anonymous users
        """
        return False

    def to_dict(self) -> dict[str, object]:
        """
        Convert user to dictionary.

        Returns:
            User data as dictionary
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "roles": self.roles,
            "permissions": self.permissions,
            "mfa_enabled": self.mfa_enabled,
            "is_authenticated": self.is_authenticated,
            "is_anonymous": self.is_anonymous,
        }

    def __str__(self) -> str:
        """String representation of user."""
        return "AnonymousUser()"

    def __repr__(self) -> str:
        """Detailed string representation of user."""
        return "AnonymousUser()"
