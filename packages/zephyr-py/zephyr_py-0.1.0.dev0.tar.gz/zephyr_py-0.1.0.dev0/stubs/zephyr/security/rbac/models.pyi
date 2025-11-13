from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Any

class Effect(str, Enum):
    ALLOW = 'allow'
    DENY = 'deny'

class Action(BaseModel):
    name: str
    description: str
    resource_type: str
    is_system: bool
    metadata: dict[str, Any]
    def validate_name(cls, v: str) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

class Resource(BaseModel):
    name: str
    resource_type: str
    description: str
    owner_id: str | None
    parent_resource: str | None
    attributes: dict[str, Any]
    is_system: bool
    metadata: dict[str, Any]
    def validate_name(cls, v: str) -> str: ...
    def get_resource_path(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

class Permission(BaseModel):
    name: str
    description: str
    resource: str
    actions: list[str]
    conditions: list[str]
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    def validate_name(cls, v: str) -> str: ...
    def validate_actions(cls, v: list[str]) -> list[str]: ...
    def has_action(self, action: str) -> bool: ...
    def matches_resource(self, resource: str) -> bool: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

class Role(BaseModel):
    name: str
    description: str
    permissions: list[str]
    parent_roles: list[str]
    child_roles: list[str]
    is_system: bool
    is_active: bool
    max_users: int | None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    def validate_name(cls, v: str) -> str: ...
    def has_permission(self, permission: str) -> bool: ...
    def add_permission(self, permission: str) -> None: ...
    def remove_permission(self, permission: str) -> None: ...
    def get_all_permissions(self, role_registry: dict[str, 'Role']) -> set[str]: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

class PolicyRule(BaseModel):
    id: str
    effect: Effect
    subjects: list[str]
    resources: list[str]
    actions: list[str]
    conditions: list[str]
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    def matches_subject(self, subject: str) -> bool: ...
    def matches_resource(self, resource: str) -> bool: ...
    def matches_action(self, action: str) -> bool: ...

class Policy(BaseModel):
    name: str
    description: str
    version: str
    rules: list[PolicyRule]
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    def add_rule(self, rule: PolicyRule) -> None: ...
    def get_active_rules(self) -> list[PolicyRule]: ...

class AccessContext(BaseModel):
    user_id: str
    user_roles: list[str]
    user_attributes: dict[str, Any]
    resource: str
    action: str
    resource_attributes: dict[str, Any]
    environment: dict[str, Any]
    request_time: datetime
    ip_address: str | None
    user_agent: str | None
    session_id: str | None
    metadata: dict[str, Any]
    def get_context_value(self, key: str) -> Any: ...

class AccessDecision(BaseModel):
    decision: Effect
    context: AccessContext
    matched_rules: list[str]
    matched_policies: list[str]
    reason: str
    confidence: float
    evaluation_time: float
    created_at: datetime
    metadata: dict[str, Any]
    def is_allowed(self) -> bool: ...
    def is_denied(self) -> bool: ...
