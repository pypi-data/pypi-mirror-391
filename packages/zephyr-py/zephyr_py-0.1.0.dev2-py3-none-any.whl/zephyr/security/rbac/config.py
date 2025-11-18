"""
RBAC configuration management.

Defines configuration options for RBAC system including policies, roles, and access control settings.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class RBACConfig(BaseModel):
    """RBAC configuration model."""

    # General settings
    enabled: bool = Field(default=True, description="Whether RBAC is enabled")
    default_deny: bool = Field(default=True, description="Default deny policy for unmatched requests")
    cache_policies: bool = Field(default=True, description="Cache policy evaluation results")
    cache_ttl: int = Field(default=300, description="Policy cache TTL in seconds")

    # Role settings
    max_roles_per_user: int = Field(default=10, description="Maximum roles per user")
    allow_role_inheritance: bool = Field(default=True, description="Allow role inheritance")
    max_inheritance_depth: int = Field(default=5, description="Maximum role inheritance depth")

    # Permission settings
    max_permissions_per_role: int = Field(default=100, description="Maximum permissions per role")
    allow_wildcard_permissions: bool = Field(default=True, description="Allow wildcard permissions")
    permission_separator: str = Field(default=":", description="Permission separator (resource:action)")

    # Policy settings
    max_policies: int = Field(default=1000, description="Maximum number of policies")
    max_rules_per_policy: int = Field(default=100, description="Maximum rules per policy")
    policy_evaluation_order: str = Field(
        default="priority", description="Policy evaluation order (priority, name, created)"
    )

    # Access control settings
    enable_audit_logging: bool = Field(default=True, description="Enable access audit logging")
    audit_log_level: str = Field(default="INFO", description="Audit log level")
    log_denied_access: bool = Field(default=True, description="Log denied access attempts")
    log_allowed_access: bool = Field(default=False, description="Log allowed access attempts")

    # Performance settings
    enable_caching: bool = Field(default=True, description="Enable RBAC caching")
    cache_size: int = Field(default=10000, description="RBAC cache size")
    cache_cleanup_interval: int = Field(default=3600, description="Cache cleanup interval in seconds")

    # Security settings
    require_explicit_allow: bool = Field(default=False, description="Require explicit allow for access")
    enable_condition_evaluation: bool = Field(default=True, description="Enable condition evaluation")
    max_condition_complexity: int = Field(default=100, description="Maximum condition complexity")

    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable RBAC metrics")
    metrics_retention_days: int = Field(default=30, description="Metrics retention in days")
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")

    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")

    @validator("policy_evaluation_order")
    def validate_policy_evaluation_order(cls, v: str) -> str:
        """Validate policy evaluation order."""
        valid_orders = ["priority", "name", "created"]
        if v not in valid_orders:
            raise ValueError(f"Policy evaluation order must be one of: {valid_orders}")
        return v

    @validator("audit_log_level")
    def validate_audit_log_level(cls, v: str) -> str:
        """Validate audit log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Audit log level must be one of: {valid_levels}")
        return v.upper()

    @validator("max_roles_per_user")
    def validate_max_roles_per_user(cls, v: int) -> int:
        """Validate max roles per user."""
        if v < 1:
            raise ValueError("Max roles per user must be at least 1")
        return v

    @validator("max_inheritance_depth")
    def validate_max_inheritance_depth(cls, v: int) -> int:
        """Validate max inheritance depth."""
        if v < 1:
            raise ValueError("Max inheritance depth must be at least 1")
        return v

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "enabled": self.enable_caching,
            "cache_policies": self.cache_policies,
            "cache_ttl": self.cache_ttl,
            "cache_size": self.cache_size,
            "cleanup_interval": self.cache_cleanup_interval,
        }

    def get_audit_config(self) -> Dict[str, Any]:
        """Get audit configuration."""
        return {
            "enabled": self.enable_audit_logging,
            "log_level": self.audit_log_level,
            "log_denied": self.log_denied_access,
            "log_allowed": self.log_allowed_access,
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return {
            "enable_metrics": self.enable_metrics,
            "enable_monitoring": self.enable_performance_monitoring,
            "metrics_retention": self.metrics_retention_days,
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "default_deny": self.default_deny,
            "require_explicit_allow": self.require_explicit_allow,
            "enable_conditions": self.enable_condition_evaluation,
            "max_condition_complexity": self.max_condition_complexity,
            "allow_wildcards": self.allow_wildcard_permissions,
        }

    def get_role_config(self) -> Dict[str, Any]:
        """Get role configuration."""
        return {
            "max_per_user": self.max_roles_per_user,
            "allow_inheritance": self.allow_role_inheritance,
            "max_inheritance_depth": self.max_inheritance_depth,
        }

    def get_policy_config(self) -> Dict[str, Any]:
        """Get policy configuration."""
        return {
            "max_policies": self.max_policies,
            "max_rules_per_policy": self.max_rules_per_policy,
            "evaluation_order": self.policy_evaluation_order,
        }

    def get_permission_config(self) -> Dict[str, Any]:
        """Get permission configuration."""
        return {
            "max_per_role": self.max_permissions_per_role,
            "allow_wildcards": self.allow_wildcard_permissions,
            "separator": self.permission_separator,
        }

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled."""
        feature_map = {
            "rbac": self.enabled,
            "caching": self.enable_caching,
            "audit_logging": self.enable_audit_logging,
            "metrics": self.enable_metrics,
            "performance_monitoring": self.enable_performance_monitoring,
            "condition_evaluation": self.enable_condition_evaluation,
            "role_inheritance": self.allow_role_inheritance,
            "wildcard_permissions": self.allow_wildcard_permissions,
        }

        return feature_map.get(feature, False)

    def get_limits(self) -> Dict[str, int]:
        """Get system limits."""
        return {
            "max_roles_per_user": self.max_roles_per_user,
            "max_permissions_per_role": self.max_permissions_per_role,
            "max_policies": self.max_policies,
            "max_rules_per_policy": self.max_rules_per_policy,
            "max_inheritance_depth": self.max_inheritance_depth,
            "cache_size": self.cache_size,
            "max_condition_complexity": self.max_condition_complexity,
        }

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add custom encoders if needed
        }
