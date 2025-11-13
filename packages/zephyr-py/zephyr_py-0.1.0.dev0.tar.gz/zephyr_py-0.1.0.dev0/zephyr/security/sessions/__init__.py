"""
Session Management for Zephyr.

Provides comprehensive session management with multiple backends including
Redis, Memory, Database, and File-based storage.
"""

from .backends import (
    SessionBackend,
    MemorySessionBackend,
    RedisSessionBackend,
    DatabaseSessionBackend,
    FileSessionBackend,
)
from .config import SessionConfig
from .models import Session, SessionData, SessionInfo, SessionStats
from .exceptions import (
    SessionError,
    SessionNotFoundError,
    SessionExpiredError,
    SessionBackendError,
    SessionSerializationError,
    SessionValidationError,
    SessionStorageError,
)
from .manager import SessionManager
from .middleware import SessionMiddleware

__all__ = [
    # Backends
    "SessionBackend",
    "MemorySessionBackend",
    "RedisSessionBackend",
    "DatabaseSessionBackend",
    "FileSessionBackend",
    # Configuration
    "SessionConfig",
    # Models
    "Session",
    "SessionData",
    "SessionInfo",
    "SessionStats",
    # Exceptions
    "SessionError",
    "SessionNotFoundError",
    "SessionExpiredError",
    "SessionBackendError",
    "SessionSerializationError",
    "SessionValidationError",
    "SessionStorageError",
    # Manager
    "SessionManager",
    # Middleware
    "SessionMiddleware",
]
