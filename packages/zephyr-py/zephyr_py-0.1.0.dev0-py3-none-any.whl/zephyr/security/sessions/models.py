"""
Session data models.

Defines all session-related data models including session data, info, and statistics.
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator


class SessionData(BaseModel):
    """Session data model."""

    data: Dict[str, Any] = Field(default_factory=dict, description="Session data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    access_count: int = Field(default=0, description="Number of times session was accessed")
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, description="Last access timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from session data."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in session data."""
        self.data[key] = value
        self.updated_at = datetime.utcnow()

    def delete(self, key: str) -> bool:
        """Delete key from session data."""
        if key in self.data:
            del self.data[key]
            self.updated_at = datetime.utcnow()
            return True
        return False

    def clear(self) -> None:
        """Clear all session data."""
        self.data.clear()
        self.updated_at = datetime.utcnow()

    def update(self, data: Dict[str, Any]) -> None:
        """Update session data with new data."""
        self.data.update(data)
        self.updated_at = datetime.utcnow()

    def keys(self) -> List[str]:
        """Get all keys in session data."""
        return list(self.data.keys())

    def values(self) -> List[Any]:
        """Get all values in session data."""
        return list(self.data.values())

    def items(self) -> List[tuple[str, Any]]:
        """Get all items in session data."""
        return list(self.data.items())

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete item by key."""
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data

    def __len__(self) -> int:
        """Get number of items."""
        return len(self.data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "metadata": self.metadata,
        }


class SessionInfo(BaseModel):
    """Session information model."""

    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, description="Last access timestamp")
    access_count: int = Field(default=0, description="Number of times session was accessed")
    is_active: bool = Field(default=True, description="Whether session is active")
    is_secure: bool = Field(default=False, description="Whether session is secure")
    is_http_only: bool = Field(default=True, description="Whether session is HTTP-only")
    same_site: str = Field(default="lax", description="SameSite attribute")
    domain: Optional[str] = Field(default=None, description="Session domain")
    path: str = Field(default="/", description="Session path")
    backend: str = Field(default="memory", description="Session backend")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("session_id")
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID."""
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()

    @validator("same_site")
    def validate_same_site(cls, v: str) -> str:
        """Validate SameSite attribute."""
        valid_values = {"strict", "lax", "none"}
        if v.lower() not in valid_values:
            raise ValueError(f"SameSite must be one of: {valid_values}")
        return v.lower()

    @validator("expires_at")
    def validate_expires_at(cls, v: datetime) -> datetime:
        """Validate expiration timestamp."""
        if v <= datetime.utcnow():
            raise ValueError("Expiration time must be in the future")
        return v

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def get_remaining_time(self) -> int:
        """Get remaining time until expiration in seconds."""
        if self.is_expired():
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())

    def get_age(self) -> int:
        """Get session age in seconds."""
        return int((datetime.utcnow() - self.created_at).total_seconds())

    def get_idle_time(self) -> int:
        """Get session idle time in seconds."""
        return int((datetime.utcnow() - self.last_accessed_at).total_seconds())

    def touch(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed_at = datetime.utcnow()
        self.access_count += 1

    def extend(self, duration: int) -> None:
        """Extend session expiration by duration in seconds."""
        self.expires_at = datetime.utcnow() + timedelta(seconds=duration)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "access_count": self.access_count,
            "is_active": self.is_active,
            "is_secure": self.is_secure,
            "is_http_only": self.is_http_only,
            "same_site": self.same_site,
            "domain": self.domain,
            "path": self.path,
            "backend": self.backend,
            "metadata": self.metadata,
        }


class Session(BaseModel):
    """Complete session model."""

    info: SessionInfo = Field(..., description="Session information")
    data: SessionData = Field(default_factory=SessionData, description="Session data")

    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self.info.session_id

    @property
    def user_id(self) -> Optional[str]:
        """Get user ID."""
        return self.info.user_id

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return self.info.is_expired()

    @property
    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.info.is_valid()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from session data."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in session data."""
        self.data.set(key, value)

    def delete(self, key: str) -> bool:
        """Delete key from session data."""
        return self.data.delete(key)

    def clear(self) -> None:
        """Clear all session data."""
        self.data.clear()

    def update(self, data: Dict[str, Any]) -> None:
        """Update session data."""
        self.data.update(data)

    def touch(self) -> None:
        """Update last accessed timestamp."""
        self.info.touch()
        self.data.last_accessed_at = datetime.utcnow()
        self.data.access_count += 1

    def extend(self, duration: int) -> None:
        """Extend session expiration."""
        self.info.extend(duration)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"info": self.info.to_dict(), "data": self.data.to_dict()}

    def to_cookie_dict(self) -> Dict[str, Any]:
        """Convert to cookie dictionary."""
        return {
            "value": self.session_id,
            "expires": self.info.expires_at,
            "secure": self.info.is_secure,
            "httponly": self.info.is_http_only,
            "samesite": self.info.same_site,
            "domain": self.info.domain,
            "path": self.info.path,
        }


class SessionStats(BaseModel):
    """Session statistics model."""

    total_sessions: int = Field(default=0, description="Total number of sessions")
    active_sessions: int = Field(default=0, description="Number of active sessions")
    expired_sessions: int = Field(default=0, description="Number of expired sessions")
    total_users: int = Field(default=0, description="Number of unique users")
    average_session_duration: float = Field(default=0.0, description="Average session duration in seconds")
    average_access_count: float = Field(default=0.0, description="Average access count per session")
    oldest_session: Optional[datetime] = Field(default=None, description="Oldest session timestamp")
    newest_session: Optional[datetime] = Field(default=None, description="Newest session timestamp")
    backend_stats: Dict[str, Any] = Field(default_factory=dict, description="Backend-specific statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Statistics timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_sessions": self.total_sessions,
            "active_sessions": self.active_sessions,
            "expired_sessions": self.expired_sessions,
            "total_users": self.total_users,
            "average_session_duration": self.average_session_duration,
            "average_access_count": self.average_access_count,
            "oldest_session": self.oldest_session.isoformat() if self.oldest_session else None,
            "newest_session": self.newest_session.isoformat() if self.newest_session else None,
            "backend_stats": self.backend_stats,
            "created_at": self.created_at.isoformat(),
        }


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return secrets.token_urlsafe(32)


def create_session(
    user_id: Optional[str] = None,
    duration: int = 3600,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    is_secure: bool = False,
    is_http_only: bool = True,
    same_site: str = "lax",
    domain: Optional[str] = None,
    path: str = "/",
    backend: str = "memory",
    **kwargs: Any,
) -> Session:
    """Create a new session."""
    session_id = generate_session_id()
    expires_at = datetime.utcnow() + timedelta(seconds=duration)

    session_info = SessionInfo(
        session_id=session_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        is_secure=is_secure,
        is_http_only=is_http_only,
        same_site=same_site,
        domain=domain,
        path=path,
        backend=backend,
        metadata=kwargs,
    )

    session_data = SessionData()

    return Session(info=session_info, data=session_data)


def create_session_from_dict(data: Dict[str, Any]) -> Session:
    """Create session from dictionary."""
    info_data = data.get("info", {})
    data_data = data.get("data", {})

    # Convert string timestamps to datetime objects
    for field in ["created_at", "expires_at", "last_accessed_at", "updated_at"]:
        if field in info_data and isinstance(info_data[field], str):
            info_data[field] = datetime.fromisoformat(info_data[field])
        if field in data_data and isinstance(data_data[field], str):
            data_data[field] = datetime.fromisoformat(data_data[field])

    session_info = SessionInfo(**info_data)
    session_data = SessionData(**data_data)

    return Session(info=session_info, data=session_data)
