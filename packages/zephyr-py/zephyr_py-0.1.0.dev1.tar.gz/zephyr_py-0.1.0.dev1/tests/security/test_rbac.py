"""
Tests for RBAC implementation.

Tests RBAC models, engine, manager, and access control functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from zephyr.security.rbac import (
    RBACManager,
    RBACConfig,
    Role,
    Permission,
    Policy,
    PolicyRule,
    AccessContext,
    AccessDecision,
    Effect,
    Action,
    Resource,
)
from zephyr.security.rbac.exceptions import (
    AccessDeniedError,
    RoleNotFoundError,
    PolicyNotFoundError,
    RBACError,
)


class TestRBACModels:
    """Test RBAC data models."""

    def test_action_creation(self):
        """Test Action model creation."""
        action = Action(name="read", description="Read action", resource_type="document", is_system=False)

        assert action.name == "read"
        assert action.description == "Read action"
        assert action.resource_type == "document"
        assert action.is_system is False

    def test_action_validation(self):
        """Test Action model validation."""
        # Test empty name
        with pytest.raises(ValueError, match="Action name cannot be empty"):
            Action(name="", description="Test")

    def test_resource_creation(self):
        """Test Resource model creation."""
        resource = Resource(
            name="document",
            resource_type="file",
            description="Document resource",
            owner_id="user123",
            parent_resource="folder1",
        )

        assert resource.name == "document"
        assert resource.resource_type == "file"
        assert resource.owner_id == "user123"
        assert resource.parent_resource == "folder1"
        assert resource.get_resource_path() == "folder1/document"

    def test_permission_creation(self):
        """Test Permission model creation."""
        permission = Permission(
            name="read_documents",
            description="Read documents permission",
            resource="documents/*",
            actions=["read", "view"],
        )

        assert permission.name == "read_documents"
        assert permission.resource == "documents/*"
        assert permission.actions == ["read", "view"]
        assert permission.has_action("read") is True
        assert permission.has_action("write") is False
        assert permission.matches_resource("documents/file1") is True
        assert permission.matches_resource("images/file1") is False

    def test_role_creation(self):
        """Test Role model creation."""
        role = Role(
            name="editor",
            description="Editor role",
            permissions=["read:documents", "write:documents"],
            parent_roles=["user"],
            is_system=False,
        )

        assert role.name == "editor"
        assert role.permissions == ["read:documents", "write:documents"]
        assert role.parent_roles == ["user"]
        assert role.has_permission("read:documents") is True
        assert role.has_permission("delete:documents") is False

    def test_role_permission_management(self):
        """Test role permission management."""
        role = Role(name="test_role")

        # Add permission
        role.add_permission("read:documents")
        assert role.has_permission("read:documents") is True

        # Remove permission
        role.remove_permission("read:documents")
        assert role.has_permission("read:documents") is False

    def test_policy_rule_creation(self):
        """Test PolicyRule model creation."""
        rule = PolicyRule(
            effect=Effect.ALLOW,
            subjects=["admin", "user"],
            resources=["documents/*"],
            actions=["read", "write"],
            priority=50,
        )

        assert rule.effect == Effect.ALLOW
        assert rule.subjects == ["admin", "user"]
        assert rule.resources == ["documents/*"]
        assert rule.actions == ["read", "write"]
        assert rule.priority == 50
        assert rule.matches_subject("admin") is True
        assert rule.matches_subject("guest") is False
        assert rule.matches_resource("documents/file1") is True
        assert rule.matches_action("read") is True

    def test_policy_creation(self):
        """Test Policy model creation."""
        policy = Policy(name="document_policy", description="Document access policy", version="1.0")

        rule = PolicyRule(effect=Effect.ALLOW, subjects=["admin"], resources=["*"], actions=["*"])

        policy.add_rule(rule)
        assert len(policy.rules) == 1
        assert policy.get_active_rules() == [rule]

    def test_access_context_creation(self):
        """Test AccessContext model creation."""
        context = AccessContext(
            user_id="user123",
            user_roles=["admin", "user"],
            resource="documents/file1",
            action="read",
            ip_address="192.168.1.1",
        )

        assert context.user_id == "user123"
        assert context.user_roles == ["admin", "user"]
        assert context.resource == "documents/file1"
        assert context.action == "read"
        assert context.ip_address == "192.168.1.1"

    def test_access_decision_creation(self):
        """Test AccessDecision model creation."""
        context = AccessContext(user_id="user123", resource="documents/file1", action="read")

        decision = AccessDecision(decision=Effect.ALLOW, context=context, reason="Access granted by policy")

        assert decision.decision == Effect.ALLOW
        assert decision.is_allowed() is True
        assert decision.is_denied() is False
        assert decision.reason == "Access granted by policy"


class TestRBACManager:
    """Test RBAC manager functionality."""

    @pytest.fixture
    def manager(self):
        """Create RBAC manager for tests."""
        return RBACManager()

    def test_manager_initialization(self, manager):
        """Test RBAC manager initialization."""
        assert manager.engine is not None
        assert manager.logger is not None

        # Check default roles are created
        assert manager.get_role("admin") is not None
        assert manager.get_role("user") is not None

    def test_role_management(self, manager):
        """Test role management."""
        # Create custom role
        custom_role = Role(
            name="custom_role", description="Custom role for testing", permissions=["read:custom", "write:custom"]
        )

        # Add role
        manager.add_role(custom_role)
        assert manager.get_role("custom_role") is not None

        # List roles
        roles = manager.list_roles()
        role_names = [role.name for role in roles]
        assert "custom_role" in role_names
        assert "admin" in role_names
        assert "user" in role_names

        # Remove role
        success = manager.remove_role("custom_role")
        assert success is True
        assert manager.get_role("custom_role") is None

    def test_role_assignment(self, manager):
        """Test role assignment to users."""
        # Assign role to user
        manager.assign_role("user123", "admin")
        assert manager.has_role("user123", "admin") is True

        # Get user roles
        roles = manager.get_user_roles("user123")
        assert "admin" in roles

        # Revoke role
        manager.revoke_role("user123", "admin")
        assert manager.has_role("user123", "admin") is False

    def test_permission_checking(self, manager):
        """Test permission checking."""
        # Assign user role
        manager.assign_role("user123", "user")

        # Check permissions
        assert manager.has_permission("user123", "read:profile") is True
        assert manager.has_permission("user123", "delete:system") is False

        # Get user permissions
        permissions = manager.get_user_permissions("user123")
        assert "read:profile" in permissions

    def test_access_control(self, manager):
        """Test access control."""
        # Assign admin role
        manager.assign_role("admin123", "admin")

        # Check access
        assert manager.is_allowed("admin123", "documents/file1", "read") is True
        assert manager.is_allowed("admin123", "documents/file1", "write") is True
        assert manager.is_allowed("admin123", "system/config", "delete") is True

        # Test require_access
        manager.require_access("admin123", "documents/file1", "read")

        # Test access denied
        with pytest.raises(AccessDeniedError):
            manager.require_access("user123", "system/config", "delete")

    def test_policy_management(self, manager):
        """Test policy management."""
        # Create custom policy
        policy = Policy(name="custom_policy", description="Custom policy for testing")

        rule = PolicyRule(
            effect=Effect.ALLOW, subjects=["custom_user"], resources=["custom/*"], actions=["read", "write"]
        )

        policy.add_rule(rule)

        # Add policy
        manager.add_policy(policy)
        assert manager.get_policy("custom_policy") is not None

        # List policies
        policies = manager.list_policies()
        policy_names = [p.name for p in policies]
        assert "custom_policy" in policy_names
        assert "default" in policy_names

        # Add rule to policy
        new_rule = PolicyRule(effect=Effect.DENY, subjects=["blocked_user"], resources=["*"], actions=["*"])

        manager.add_policy_rule("custom_policy", new_rule)
        policy = manager.get_policy("custom_policy")
        assert len(policy.rules) == 2

        # Remove policy
        success = manager.remove_policy("custom_policy")
        assert success is True
        assert manager.get_policy("custom_policy") is None

    def test_access_context_evaluation(self, manager):
        """Test access context evaluation."""
        context = AccessContext(
            user_id="user123", user_roles=["user"], resource="documents/file1", action="read", ip_address="192.168.1.1"
        )

        # Assign user role
        manager.assign_role("user123", "user")

        # Check access
        decision = manager.check_access(context)
        assert decision.is_allowed() is True
        assert decision.context == context

    def test_user_info(self, manager):
        """Test user information retrieval."""
        # Assign roles to user
        manager.assign_role("user123", "admin")
        manager.assign_role("user123", "user")

        # Get user info
        info = manager.get_user_info("user123")
        assert info["user_id"] == "user123"
        assert "admin" in info["roles"]
        assert "user" in info["roles"]
        assert info["role_count"] == 2
        assert info["permission_count"] > 0

    def test_role_info(self, manager):
        """Test role information retrieval."""
        info = manager.get_role_info("admin")
        assert info is not None
        assert info["name"] == "admin"
        assert info["is_system"] is True
        assert info["is_active"] is True
        assert "permissions" in info
        assert "user_count" in info

    def test_policy_info(self, manager):
        """Test policy information retrieval."""
        info = manager.get_policy_info("default")
        assert info is not None
        assert info["name"] == "default"
        assert info["is_system"] is True
        assert info["is_active"] is True
        assert info["rule_count"] > 0
        assert info["active_rule_count"] > 0

    def test_system_stats(self, manager):
        """Test system statistics."""
        stats = manager.get_stats()

        assert "roles" in stats
        assert "policies" in stats
        assert "users" in stats

        assert stats["roles"]["total"] >= 2  # admin and user
        assert stats["policies"]["total"] >= 1  # default
        assert stats["users"]["total"] >= 0

    def test_role_hierarchy_validation(self, manager):
        """Test role hierarchy validation."""
        # Create roles with hierarchy
        parent_role = Role(name="parent_role", description="Parent role")
        child_role = Role(name="child_role", description="Child role", parent_roles=["parent_role"])

        manager.add_role(parent_role)
        manager.add_role(child_role)

        # Validate hierarchy
        circular_deps = manager.validate_role_hierarchy("child_role")
        assert len(circular_deps) == 0

        # Test circular dependency
        parent_role.parent_roles = ["child_role"]  # Create circular dependency
        manager.add_role(parent_role)  # Update role

        circular_deps = manager.validate_role_hierarchy("child_role")
        assert len(circular_deps) > 0

    def test_cleanup_inactive_roles(self, manager):
        """Test cleanup of inactive roles."""
        # Create inactive role
        inactive_role = Role(name="inactive_role", description="Inactive role", is_active=False)

        manager.add_role(inactive_role)
        assert manager.get_role("inactive_role") is not None

        # Cleanup inactive roles
        cleaned_count = manager.cleanup_inactive_roles()
        assert cleaned_count == 1
        assert manager.get_role("inactive_role") is None

    def test_cleanup_inactive_policies(self, manager):
        """Test cleanup of inactive policies."""
        # Create inactive policy
        inactive_policy = Policy(name="inactive_policy", description="Inactive policy", is_active=False)

        manager.add_policy(inactive_policy)
        assert manager.get_policy("inactive_policy") is not None

        # Cleanup inactive policies
        cleaned_count = manager.cleanup_inactive_policies()
        assert cleaned_count == 1
        assert manager.get_policy("inactive_policy") is None


class TestRBACConfig:
    """Test RBAC configuration."""

    def test_default_config(self):
        """Test default RBAC configuration."""
        config = RBACConfig()

        assert config.enabled is True
        assert config.default_deny is True
        assert config.cache_policies is True
        assert config.cache_ttl == 300
        assert config.max_roles_per_user == 10
        assert config.allow_role_inheritance is True
        assert config.max_inheritance_depth == 5
        assert config.max_permissions_per_role == 100
        assert config.allow_wildcard_permissions is True
        assert config.permission_separator == ":"
        assert config.max_policies == 1000
        assert config.max_rules_per_policy == 100
        assert config.policy_evaluation_order == "priority"
        assert config.enable_audit_logging is True
        assert config.audit_log_level == "INFO"
        assert config.log_denied_access is True
        assert config.log_allowed_access is False
        assert config.enable_caching is True
        assert config.cache_size == 10000
        assert config.cache_cleanup_interval == 3600
        assert config.require_explicit_allow is False
        assert config.enable_condition_evaluation is True
        assert config.max_condition_complexity == 100
        assert config.enable_metrics is True
        assert config.metrics_retention_days == 30
        assert config.enable_performance_monitoring is True

    def test_custom_config(self):
        """Test custom RBAC configuration."""
        config = RBACConfig(
            enabled=False,
            default_deny=False,
            cache_policies=False,
            cache_ttl=600,
            max_roles_per_user=5,
            allow_role_inheritance=False,
            max_inheritance_depth=3,
            max_permissions_per_role=50,
            allow_wildcard_permissions=False,
            permission_separator=".",
            max_policies=500,
            max_rules_per_policy=50,
            policy_evaluation_order="name",
            enable_audit_logging=False,
            audit_log_level="ERROR",
            log_denied_access=False,
            log_allowed_access=True,
            enable_caching=False,
            cache_size=5000,
            cache_cleanup_interval=1800,
            require_explicit_allow=True,
            enable_condition_evaluation=False,
            max_condition_complexity=50,
            enable_metrics=False,
            metrics_retention_days=7,
            enable_performance_monitoring=False,
        )

        assert config.enabled is False
        assert config.default_deny is False
        assert config.cache_policies is False
        assert config.cache_ttl == 600
        assert config.max_roles_per_user == 5
        assert config.allow_role_inheritance is False
        assert config.max_inheritance_depth == 3
        assert config.max_permissions_per_role == 50
        assert config.allow_wildcard_permissions is False
        assert config.permission_separator == "."
        assert config.max_policies == 500
        assert config.max_rules_per_policy == 50
        assert config.policy_evaluation_order == "name"
        assert config.enable_audit_logging is False
        assert config.audit_log_level == "ERROR"
        assert config.log_denied_access is False
        assert config.log_allowed_access is True
        assert config.enable_caching is False
        assert config.cache_size == 5000
        assert config.cache_cleanup_interval == 1800
        assert config.require_explicit_allow is True
        assert config.enable_condition_evaluation is False
        assert config.max_condition_complexity == 50
        assert config.enable_metrics is False
        assert config.metrics_retention_days == 7
        assert config.enable_performance_monitoring is False

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid policy evaluation order
        with pytest.raises(ValueError, match="Policy evaluation order must be one of"):
            RBACConfig(policy_evaluation_order="invalid")

        # Test invalid audit log level
        with pytest.raises(ValueError, match="Audit log level must be one of"):
            RBACConfig(audit_log_level="invalid")

        # Test invalid max roles per user
        with pytest.raises(ValueError, match="Max roles per user must be at least 1"):
            RBACConfig(max_roles_per_user=0)

        # Test invalid max inheritance depth
        with pytest.raises(ValueError, match="Max inheritance depth must be at least 1"):
            RBACConfig(max_inheritance_depth=0)

    def test_config_methods(self):
        """Test configuration utility methods."""
        config = RBACConfig()

        # Test cache config
        cache_config = config.get_cache_config()
        assert cache_config["enabled"] is True
        assert cache_config["cache_policies"] is True
        assert cache_config["cache_ttl"] == 300
        assert cache_config["cache_size"] == 10000
        assert cache_config["cleanup_interval"] == 3600

        # Test audit config
        audit_config = config.get_audit_config()
        assert audit_config["enabled"] is True
        assert audit_config["log_level"] == "INFO"
        assert audit_config["log_denied"] is True
        assert audit_config["log_allowed"] is False

        # Test performance config
        perf_config = config.get_performance_config()
        assert perf_config["enable_metrics"] is True
        assert perf_config["enable_monitoring"] is True
        assert perf_config["metrics_retention"] == 30

        # Test security config
        security_config = config.get_security_config()
        assert security_config["default_deny"] is True
        assert security_config["require_explicit_allow"] is False
        assert security_config["enable_conditions"] is True
        assert security_config["max_condition_complexity"] == 100
        assert security_config["allow_wildcards"] is True

        # Test role config
        role_config = config.get_role_config()
        assert role_config["max_per_user"] == 10
        assert role_config["allow_inheritance"] is True
        assert role_config["max_inheritance_depth"] == 5

        # Test policy config
        policy_config = config.get_policy_config()
        assert policy_config["max_policies"] == 1000
        assert policy_config["max_rules_per_policy"] == 100
        assert policy_config["evaluation_order"] == "priority"

        # Test permission config
        perm_config = config.get_permission_config()
        assert perm_config["max_per_role"] == 100
        assert perm_config["allow_wildcards"] is True
        assert perm_config["separator"] == ":"

        # Test feature enabled check
        assert config.is_feature_enabled("rbac") is True
        assert config.is_feature_enabled("caching") is True
        assert config.is_feature_enabled("audit_logging") is True
        assert config.is_feature_enabled("metrics") is True
        assert config.is_feature_enabled("invalid_feature") is False

        # Test limits
        limits = config.get_limits()
        assert limits["max_roles_per_user"] == 10
        assert limits["max_permissions_per_role"] == 100
        assert limits["max_policies"] == 1000
        assert limits["max_rules_per_policy"] == 100
        assert limits["max_inheritance_depth"] == 5
        assert limits["cache_size"] == 10000
        assert limits["max_condition_complexity"] == 100
