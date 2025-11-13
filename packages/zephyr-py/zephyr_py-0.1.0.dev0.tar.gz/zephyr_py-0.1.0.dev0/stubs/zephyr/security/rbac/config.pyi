from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class RBACConfig(BaseModel):
    enabled: bool
    default_deny: bool
    cache_policies: bool
    cache_ttl: int
    max_roles_per_user: int
    allow_role_inheritance: bool
    max_inheritance_depth: int
    max_permissions_per_role: int
    allow_wildcard_permissions: bool
    permission_separator: str
    max_policies: int
    max_rules_per_policy: int
    policy_evaluation_order: str
    enable_audit_logging: bool
    audit_log_level: str
    log_denied_access: bool
    log_allowed_access: bool
    enable_caching: bool
    cache_size: int
    cache_cleanup_interval: int
    require_explicit_allow: bool
    enable_condition_evaluation: bool
    max_condition_complexity: int
    enable_metrics: bool
    metrics_retention_days: int
    enable_performance_monitoring: bool
    custom_settings: dict[str, Any]
    def validate_policy_evaluation_order(cls, v: str) -> str: ...
    def validate_audit_log_level(cls, v: str) -> str: ...
    def validate_max_roles_per_user(cls, v: int) -> int: ...
    def validate_max_inheritance_depth(cls, v: int) -> int: ...
    def get_cache_config(self) -> dict[str, Any]: ...
    def get_audit_config(self) -> dict[str, Any]: ...
    def get_performance_config(self) -> dict[str, Any]: ...
    def get_security_config(self) -> dict[str, Any]: ...
    def get_role_config(self) -> dict[str, Any]: ...
    def get_policy_config(self) -> dict[str, Any]: ...
    def get_permission_config(self) -> dict[str, Any]: ...
    def is_feature_enabled(self, feature: str) -> bool: ...
    def get_limits(self) -> dict[str, int]: ...
    class Config:
        json_encoders: Incomplete
