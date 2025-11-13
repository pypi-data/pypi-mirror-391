"""
Session configuration management.

Defines configuration options for session management including backends, security, and performance settings.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class SessionConfig(BaseModel):
    """Session configuration model."""

    # General settings
    enabled: bool = Field(default=True, description="Whether sessions are enabled")
    secret_key: str = Field(..., description="Secret key for session encryption")
    session_cookie_name: str = Field(default="zephyr_session", description="Session cookie name")
    session_cookie_path: str = Field(default="/", description="Session cookie path")
    session_cookie_domain: Optional[str] = Field(default=None, description="Session cookie domain")
    session_cookie_secure: bool = Field(default=False, description="Secure cookie flag")
    session_cookie_httponly: bool = Field(default=True, description="HTTP-only cookie flag")
    session_cookie_samesite: str = Field(default="lax", description="SameSite cookie attribute")

    # Session duration settings
    session_lifetime: int = Field(default=3600, description="Session lifetime in seconds")
    session_idle_timeout: int = Field(default=1800, description="Session idle timeout in seconds")
    session_absolute_timeout: int = Field(default=86400, description="Absolute session timeout in seconds")
    session_rolling: bool = Field(default=True, description="Rolling session expiration")
    session_auto_extend: bool = Field(default=False, description="Auto-extend session on access")

    # Backend settings
    backend: str = Field(default="memory", description="Session backend (memory, redis, database, file)")
    backend_config: Dict[str, Any] = Field(default_factory=dict, description="Backend-specific configuration")

    # Memory backend settings
    memory_max_sessions: int = Field(default=10000, description="Maximum sessions in memory")
    memory_cleanup_interval: int = Field(default=300, description="Memory cleanup interval in seconds")

    # Redis backend settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_key_prefix: str = Field(default="zephyr:session:", description="Redis key prefix")
    redis_connection_pool_size: int = Field(default=10, description="Redis connection pool size")
    redis_socket_timeout: int = Field(default=5, description="Redis socket timeout in seconds")
    redis_socket_connect_timeout: int = Field(default=5, description="Redis socket connect timeout in seconds")
    redis_retry_on_timeout: bool = Field(default=True, description="Retry on Redis timeout")
    redis_max_connections: int = Field(default=20, description="Maximum Redis connections")

    # Database backend settings
    database_url: str = Field(default="sqlite:///sessions.db", description="Database connection URL")
    database_table_name: str = Field(default="sessions", description="Database table name")
    database_cleanup_interval: int = Field(default=3600, description="Database cleanup interval in seconds")
    database_connection_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")

    # File backend settings
    file_path: str = Field(default="./sessions", description="File storage path")
    file_cleanup_interval: int = Field(default=3600, description="File cleanup interval in seconds")
    file_max_sessions: int = Field(default=100000, description="Maximum sessions in file storage")
    file_compression: bool = Field(default=True, description="Enable file compression")

    # Security settings
    encrypt_session_data: bool = Field(default=True, description="Encrypt session data")
    encryption_algorithm: str = Field(default="AES-256-GCM", description="Encryption algorithm")
    encryption_key_rotation: bool = Field(default=False, description="Enable encryption key rotation")
    encryption_key_rotation_interval: int = Field(default=86400, description="Key rotation interval in seconds")

    # Serialization settings
    serializer: str = Field(default="json", description="Session serializer (json, pickle, msgpack)")
    compress_session_data: bool = Field(default=False, description="Compress session data")
    compression_level: int = Field(default=6, description="Compression level (1-9)")
    max_session_size: int = Field(default=4096, description="Maximum session size in bytes")

    # Performance settings
    enable_caching: bool = Field(default=True, description="Enable session caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")
    cache_cleanup_interval: int = Field(default=600, description="Cache cleanup interval in seconds")

    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable session metrics")
    enable_audit_logging: bool = Field(default=False, description="Enable audit logging")
    metrics_retention_days: int = Field(default=30, description="Metrics retention in days")
    log_session_creation: bool = Field(default=False, description="Log session creation")
    log_session_destruction: bool = Field(default=False, description="Log session destruction")
    log_session_access: bool = Field(default=False, description="Log session access")

    # Cleanup settings
    cleanup_expired_sessions: bool = Field(default=True, description="Cleanup expired sessions")
    cleanup_interval: int = Field(default=3600, description="Cleanup interval in seconds")
    cleanup_batch_size: int = Field(default=100, description="Cleanup batch size")
    cleanup_max_workers: int = Field(default=4, description="Maximum cleanup workers")

    # Validation settings
    validate_session_data: bool = Field(default=True, description="Validate session data")
    max_session_keys: int = Field(default=100, description="Maximum number of session keys")
    allowed_session_types: List[str] = Field(
        default_factory=lambda: ["str", "int", "float", "bool", "list", "dict"],
        description="Allowed session data types",
    )

    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")

    @validator("session_cookie_samesite")
    def validate_same_site(cls, v: str) -> str:
        """Validate SameSite attribute."""
        valid_values = {"strict", "lax", "none"}
        if v.lower() not in valid_values:
            raise ValueError(f"SameSite must be one of: {valid_values}")
        return v.lower()

    @validator("backend")
    def validate_backend(cls, v: str) -> str:
        """Validate session backend."""
        valid_backends = {"memory", "redis", "database", "file"}
        if v.lower() not in valid_backends:
            raise ValueError(f"Backend must be one of: {valid_backends}")
        return v.lower()

    @validator("serializer")
    def validate_serializer(cls, v: str) -> str:
        """Validate serializer."""
        valid_serializers = {"json", "pickle", "msgpack"}
        if v.lower() not in valid_serializers:
            raise ValueError(f"Serializer must be one of: {valid_serializers}")
        return v.lower()

    @validator("encryption_algorithm")
    def validate_encryption_algorithm(cls, v: str) -> str:
        """Validate encryption algorithm."""
        valid_algorithms = {"AES-256-GCM", "AES-256-CBC", "AES-128-GCM", "AES-128-CBC"}
        if v.upper() not in valid_algorithms:
            raise ValueError(f"Encryption algorithm must be one of: {valid_algorithms}")
        return v.upper()

    @validator("compression_level")
    def validate_compression_level(cls, v: int) -> int:
        """Validate compression level."""
        if not 1 <= v <= 9:
            raise ValueError("Compression level must be between 1 and 9")
        return v

    @validator("session_lifetime")
    def validate_session_lifetime(cls, v: int) -> int:
        """Validate session lifetime."""
        if v <= 0:
            raise ValueError("Session lifetime must be positive")
        return v

    @validator("session_idle_timeout")
    def validate_session_idle_timeout(cls, v: int) -> int:
        """Validate session idle timeout."""
        if v <= 0:
            raise ValueError("Session idle timeout must be positive")
        return v

    @validator("session_absolute_timeout")
    def validate_session_absolute_timeout(cls, v: int) -> int:
        """Validate session absolute timeout."""
        if v <= 0:
            raise ValueError("Session absolute timeout must be positive")
        return v

    def get_backend_config(self) -> Dict[str, Any]:
        """Get backend-specific configuration."""
        backend = self.backend.lower()

        if backend == "memory":
            return {"max_sessions": self.memory_max_sessions, "cleanup_interval": self.memory_cleanup_interval}
        elif backend == "redis":
            return {
                "url": self.redis_url,
                "key_prefix": self.redis_key_prefix,
                "connection_pool_size": self.redis_connection_pool_size,
                "socket_timeout": self.redis_socket_timeout,
                "socket_connect_timeout": self.redis_socket_connect_timeout,
                "retry_on_timeout": self.redis_retry_on_timeout,
                "max_connections": self.redis_max_connections,
                **self.backend_config,
            }
        elif backend == "database":
            return {
                "url": self.database_url,
                "table_name": self.database_table_name,
                "cleanup_interval": self.database_cleanup_interval,
                "connection_pool_size": self.database_connection_pool_size,
                "max_overflow": self.database_max_overflow,
                **self.backend_config,
            }
        elif backend == "file":
            return {
                "path": self.file_path,
                "cleanup_interval": self.file_cleanup_interval,
                "max_sessions": self.file_max_sessions,
                "compression": self.file_compression,
                **self.backend_config,
            }
        else:
            return self.backend_config

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "encrypt_data": self.encrypt_session_data,
            "algorithm": self.encryption_algorithm,
            "key_rotation": self.encryption_key_rotation,
            "key_rotation_interval": self.encryption_key_rotation_interval,
            "secret_key": self.secret_key,
        }

    def get_cookie_config(self) -> Dict[str, Any]:
        """Get cookie configuration."""
        return {
            "name": self.session_cookie_name,
            "path": self.session_cookie_path,
            "domain": self.session_cookie_domain,
            "secure": self.session_cookie_secure,
            "httponly": self.session_cookie_httponly,
            "samesite": self.session_cookie_samesite,
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return {
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "cache_max_size": self.cache_max_size,
            "cache_cleanup_interval": self.cache_cleanup_interval,
            "compress_data": self.compress_session_data,
            "compression_level": self.compression_level,
            "max_session_size": self.max_session_size,
        }

    def get_cleanup_config(self) -> Dict[str, Any]:
        """Get cleanup configuration."""
        return {
            "cleanup_expired": self.cleanup_expired_sessions,
            "cleanup_interval": self.cleanup_interval,
            "cleanup_batch_size": self.cleanup_batch_size,
            "cleanup_max_workers": self.cleanup_max_workers,
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            "enable_metrics": self.enable_metrics,
            "enable_audit_logging": self.enable_audit_logging,
            "metrics_retention_days": self.metrics_retention_days,
            "log_session_creation": self.log_session_creation,
            "log_session_destruction": self.log_session_destruction,
            "log_session_access": self.log_session_access,
        }

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration."""
        return {
            "validate_data": self.validate_session_data,
            "max_keys": self.max_session_keys,
            "allowed_types": self.allowed_session_types,
        }

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled."""
        feature_map = {
            "sessions": self.enabled,
            "caching": self.enable_caching,
            "encryption": self.encrypt_session_data,
            "compression": self.compress_session_data,
            "metrics": self.enable_metrics,
            "audit_logging": self.enable_audit_logging,
            "cleanup": self.cleanup_expired_sessions,
            "validation": self.validate_session_data,
            "rolling": self.session_rolling,
            "auto_extend": self.session_auto_extend,
        }

        return feature_map.get(feature, False)

    def get_limits(self) -> Dict[str, int]:
        """Get system limits."""
        return {
            "session_lifetime": self.session_lifetime,
            "session_idle_timeout": self.session_idle_timeout,
            "session_absolute_timeout": self.session_absolute_timeout,
            "max_session_size": self.max_session_size,
            "max_session_keys": self.max_session_keys,
            "memory_max_sessions": self.memory_max_sessions,
            "file_max_sessions": self.file_max_sessions,
            "cache_max_size": self.cache_max_size,
            "cleanup_batch_size": self.cleanup_batch_size,
            "cleanup_max_workers": self.cleanup_max_workers,
        }

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add custom encoders if needed
        }
