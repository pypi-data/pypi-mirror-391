"""
Tests for user models.

Tests User and AnonymousUser functionality, roles, and permissions.
"""

import pytest

from zephyr.security.user import User, AnonymousUser


class TestUser:
    """Test User model functionality."""

    @pytest.fixture
    def user(self):
        """Create user for tests."""
        return User(
            id="user123",
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            roles=["admin", "user"],
            permissions=["read", "write", "delete"],
            mfa_enabled=False,
        )

    def test_user_creation(self, user):
        """Test user creation with all attributes."""
        assert user.id == "user123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.roles == ["admin", "user"]
        assert user.permissions == ["read", "write", "delete"]
        assert user.mfa_enabled is False

    def test_user_creation_with_defaults(self):
        """Test user creation with default values."""
        user = User(id="user456", username="simpleuser", email="simple@example.com")

        assert user.id == "user456"
        assert user.username == "simpleuser"
        assert user.email == "simple@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.roles == []
        assert user.permissions == []
        assert user.mfa_enabled is False

    def test_is_authenticated(self, user):
        """Test is_authenticated property."""
        assert user.is_authenticated is True

    def test_is_anonymous(self, user):
        """Test is_anonymous property."""
        assert user.is_anonymous is False

    @pytest.mark.asyncio
    async def test_has_permission_success(self, user):
        """Test successful permission check."""
        has_permission = await user.has_permission("read")
        assert has_permission is True

    @pytest.mark.asyncio
    async def test_has_permission_failure(self, user):
        """Test failed permission check."""
        has_permission = await user.has_permission("nonexistent")
        assert has_permission is False

    @pytest.mark.asyncio
    async def test_has_permission_empty(self, user):
        """Test permission check with empty permission."""
        has_permission = await user.has_permission("")
        assert has_permission is False

    @pytest.mark.asyncio
    async def test_has_permission_superuser(self):
        """Test that superuser has all permissions."""
        superuser = User(
            id="super123",
            username="superuser",
            email="super@example.com",
            is_superuser=True,
            permissions=[],  # No specific permissions
        )

        has_permission = await superuser.has_permission("any_permission")
        assert has_permission is True

    @pytest.mark.asyncio
    async def test_has_role_success(self, user):
        """Test successful role check."""
        has_role = await user.has_role("admin")
        assert has_role is True

    @pytest.mark.asyncio
    async def test_has_role_failure(self, user):
        """Test failed role check."""
        has_role = await user.has_role("nonexistent")
        assert has_role is False

    @pytest.mark.asyncio
    async def test_has_role_empty(self, user):
        """Test role check with empty role."""
        has_role = await user.has_role("")
        assert has_role is False

    @pytest.mark.asyncio
    async def test_has_any_role_success(self, user):
        """Test successful any role check."""
        has_any_role = await user.has_any_role(["admin", "nonexistent"])
        assert has_any_role is True

    @pytest.mark.asyncio
    async def test_has_any_role_failure(self, user):
        """Test failed any role check."""
        has_any_role = await user.has_any_role(["nonexistent1", "nonexistent2"])
        assert has_any_role is False

    @pytest.mark.asyncio
    async def test_has_any_role_empty_list(self, user):
        """Test any role check with empty list."""
        has_any_role = await user.has_any_role([])
        assert has_any_role is False

    @pytest.mark.asyncio
    async def test_has_all_roles_success(self, user):
        """Test successful all roles check."""
        has_all_roles = await user.has_all_roles(["admin", "user"])
        assert has_all_roles is True

    @pytest.mark.asyncio
    async def test_has_all_roles_failure(self, user):
        """Test failed all roles check."""
        has_all_roles = await user.has_all_roles(["admin", "nonexistent"])
        assert has_all_roles is False

    @pytest.mark.asyncio
    async def test_has_all_roles_empty_list(self, user):
        """Test all roles check with empty list."""
        has_all_roles = await user.has_all_roles([])
        assert has_all_roles is True

    @pytest.mark.asyncio
    async def test_has_any_permission_success(self, user):
        """Test successful any permission check."""
        has_any_permission = await user.has_any_permission(["read", "nonexistent"])
        assert has_any_permission is True

    @pytest.mark.asyncio
    async def test_has_any_permission_failure(self, user):
        """Test failed any permission check."""
        has_any_permission = await user.has_any_permission(["nonexistent1", "nonexistent2"])
        assert has_any_permission is False

    @pytest.mark.asyncio
    async def test_has_any_permission_empty_list(self, user):
        """Test any permission check with empty list."""
        has_any_permission = await user.has_any_permission([])
        assert has_any_permission is False

    @pytest.mark.asyncio
    async def test_has_all_permissions_success(self, user):
        """Test successful all permissions check."""
        has_all_permissions = await user.has_all_permissions(["read", "write"])
        assert has_all_permissions is True

    @pytest.mark.asyncio
    async def test_has_all_permissions_failure(self, user):
        """Test failed all permissions check."""
        has_all_permissions = await user.has_all_permissions(["read", "nonexistent"])
        assert has_all_permissions is False

    @pytest.mark.asyncio
    async def test_has_all_permissions_empty_list(self, user):
        """Test all permissions check with empty list."""
        has_all_permissions = await user.has_all_permissions([])
        assert has_all_permissions is True

    def test_to_dict(self, user):
        """Test user to dictionary conversion."""
        user_dict = user.to_dict()

        assert user_dict["id"] == "user123"
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["is_active"] is True
        assert user_dict["is_superuser"] is False
        assert user_dict["roles"] == ["admin", "user"]
        assert user_dict["permissions"] == ["read", "write", "delete"]
        assert user_dict["mfa_enabled"] is False
        assert user_dict["is_authenticated"] is True
        assert user_dict["is_anonymous"] is False

    def test_str_representation(self, user):
        """Test string representation of user."""
        user_str = str(user)
        assert "User(id=user123" in user_str
        assert "username=testuser" in user_str
        assert "email=test@example.com" in user_str

    def test_repr_representation(self, user):
        """Test detailed string representation of user."""
        user_repr = repr(user)
        assert "User(id=user123" in user_repr
        assert "username=testuser" in user_repr
        assert "email=test@example.com" in user_repr
        assert "is_active=True" in user_repr
        assert "is_superuser=False" in user_repr
        assert "roles=['admin', 'user']" in user_repr
        assert "permissions=['read', 'write', 'delete']" in user_repr
        assert "mfa_enabled=False" in user_repr


class TestAnonymousUser:
    """Test AnonymousUser model functionality."""

    @pytest.fixture
    def anon_user(self):
        """Create anonymous user for tests."""
        return AnonymousUser()

    def test_anonymous_user_creation(self, anon_user):
        """Test anonymous user creation."""
        assert anon_user.id is None
        assert anon_user.username is None
        assert anon_user.email is None
        assert anon_user.is_active is False
        assert anon_user.is_superuser is False
        assert anon_user.roles == []
        assert anon_user.permissions == []
        assert anon_user.mfa_enabled is False

    def test_is_authenticated(self, anon_user):
        """Test is_authenticated property."""
        assert anon_user.is_authenticated is False

    def test_is_anonymous(self, anon_user):
        """Test is_anonymous property."""
        assert anon_user.is_anonymous is True

    @pytest.mark.asyncio
    async def test_has_permission_always_false(self, anon_user):
        """Test that anonymous user never has permissions."""
        has_permission = await anon_user.has_permission("any_permission")
        assert has_permission is False

    @pytest.mark.asyncio
    async def test_has_role_always_false(self, anon_user):
        """Test that anonymous user never has roles."""
        has_role = await anon_user.has_role("any_role")
        assert has_role is False

    @pytest.mark.asyncio
    async def test_has_any_role_always_false(self, anon_user):
        """Test that anonymous user never has any roles."""
        has_any_role = await anon_user.has_any_role(["role1", "role2"])
        assert has_any_role is False

    @pytest.mark.asyncio
    async def test_has_all_roles_always_false(self, anon_user):
        """Test that anonymous user never has all roles."""
        has_all_roles = await anon_user.has_all_roles(["role1", "role2"])
        assert has_all_roles is False

    @pytest.mark.asyncio
    async def test_has_any_permission_always_false(self, anon_user):
        """Test that anonymous user never has any permissions."""
        has_any_permission = await anon_user.has_any_permission(["perm1", "perm2"])
        assert has_any_permission is False

    @pytest.mark.asyncio
    async def test_has_all_permissions_always_false(self, anon_user):
        """Test that anonymous user never has all permissions."""
        has_all_permissions = await anon_user.has_all_permissions(["perm1", "perm2"])
        assert has_all_permissions is False

    def test_to_dict(self, anon_user):
        """Test anonymous user to dictionary conversion."""
        user_dict = anon_user.to_dict()

        assert user_dict["id"] is None
        assert user_dict["username"] is None
        assert user_dict["email"] is None
        assert user_dict["is_active"] is False
        assert user_dict["is_superuser"] is False
        assert user_dict["roles"] == []
        assert user_dict["permissions"] == []
        assert user_dict["mfa_enabled"] is False
        assert user_dict["is_authenticated"] is False
        assert user_dict["is_anonymous"] is True

    def test_str_representation(self, anon_user):
        """Test string representation of anonymous user."""
        user_str = str(anon_user)
        assert user_str == "AnonymousUser()"

    def test_repr_representation(self, anon_user):
        """Test detailed string representation of anonymous user."""
        user_repr = repr(anon_user)
        assert user_repr == "AnonymousUser()"


class TestUserComparison:
    """Test user comparison and equality."""

    def test_user_equality(self):
        """Test user equality based on ID."""
        user1 = User(id="user123", username="user1", email="user1@example.com")
        user2 = User(id="user123", username="user2", email="user2@example.com")
        user3 = User(id="user456", username="user1", email="user1@example.com")

        # Same ID should be equal (if we implement __eq__)
        # For now, just test that they have the same ID
        assert user1.id == user2.id
        assert user1.id != user3.id

    def test_anonymous_user_equality(self):
        """Test anonymous user equality."""
        anon1 = AnonymousUser()
        anon2 = AnonymousUser()

        # All anonymous users should be equal (if we implement __eq__)
        # For now, just test that they have the same properties
        assert anon1.is_anonymous == anon2.is_anonymous
        assert anon1.is_authenticated == anon2.is_authenticated


class TestUserEdgeCases:
    """Test user model edge cases."""

    @pytest.mark.asyncio
    async def test_user_with_none_values(self):
        """Test user with None values in roles and permissions."""
        user = User(id="user123", username="testuser", email="test@example.com", roles=None, permissions=None)

        # Should default to empty lists
        assert user.roles == []
        assert user.permissions == []

        # Should still work with permission checks
        has_permission = await user.has_permission("any_permission")
        assert has_permission is False

    @pytest.mark.asyncio
    async def test_user_with_empty_strings(self):
        """Test user with empty string values."""
        user = User(id="", username="", email="", roles=[], permissions=[])

        assert user.id == ""
        assert user.username == ""
        assert user.email == ""

        # Should still work with permission checks
        has_permission = await user.has_permission("any_permission")
        assert has_permission is False
