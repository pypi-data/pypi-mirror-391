"""
Session management exceptions and error handling.

Defines all session-specific exceptions with proper error codes and descriptions.
"""

from typing import Any, Dict, Optional


class SessionError(Exception):
    """Base session error class."""

    def __init__(
        self, message: str, error_code: str | None = None, session_id: str | None = None, **kwargs: Any
    ) -> None:
        """
        Initialize session error.

        Args:
            message: Error message
            error_code: Error code
            session_id: Session ID
            **kwargs: Additional error parameters
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.session_id = session_id
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        result = {"error": "session_error", "message": self.message}

        if self.error_code:
            result["error_code"] = self.error_code
        if self.session_id:
            result["session_id"] = self.session_id

        result.update(self.extra)
        return result


class SessionNotFoundError(SessionError):
    """Session not found error."""

    def __init__(self, session_id: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Session '{session_id}' not found", error_code="session_not_found", session_id=session_id, **kwargs
        )


class SessionExpiredError(SessionError):
    """Session expired error."""

    def __init__(self, session_id: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Session '{session_id}' has expired", error_code="session_expired", session_id=session_id, **kwargs
        )


class SessionBackendError(SessionError):
    """Session backend error."""

    def __init__(self, message: str, backend: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_backend_error", backend=backend, **kwargs)


class SessionSerializationError(SessionError):
    """Session serialization error."""

    def __init__(self, message: str, session_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_serialization_error", session_id=session_id, **kwargs)


class SessionValidationError(SessionError):
    """Session validation error."""

    def __init__(self, message: str, session_id: str | None = None, field: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            message=message, error_code="session_validation_error", session_id=session_id, field=field, **kwargs
        )


class SessionStorageError(SessionError):
    """Session storage error."""

    def __init__(self, message: str, backend: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_storage_error", backend=backend, **kwargs)


class SessionConfigurationError(SessionError):
    """Session configuration error."""

    def __init__(self, message: str, config_key: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_configuration_error", config_key=config_key, **kwargs)


class SessionBackendNotAvailableError(SessionError):
    """Session backend not available error."""

    def __init__(self, backend: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Session backend '{backend}' is not available",
            error_code="session_backend_not_available",
            backend=backend,
            **kwargs,
        )


class SessionDataTooLargeError(SessionError):
    """Session data too large error."""

    def __init__(self, session_id: str, size: int | None = None, max_size: int | None = None, **kwargs: Any) -> None:
        message = f"Session data too large"
        if size and max_size:
            message += f" ({size} bytes > {max_size} bytes)"

        super().__init__(
            message=message,
            error_code="session_data_too_large",
            session_id=session_id,
            size=size,
            max_size=max_size,
            **kwargs,
        )


class SessionConcurrencyError(SessionError):
    """Session concurrency error."""

    def __init__(self, session_id: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Session '{session_id}' is being accessed concurrently",
            error_code="session_concurrency_error",
            session_id=session_id,
            **kwargs,
        )


class SessionLockError(SessionError):
    """Session lock error."""

    def __init__(self, session_id: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Failed to lock session '{session_id}'",
            error_code="session_lock_error",
            session_id=session_id,
            **kwargs,
        )


class SessionUnlockError(SessionError):
    """Session unlock error."""

    def __init__(self, session_id: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Failed to unlock session '{session_id}'",
            error_code="session_unlock_error",
            session_id=session_id,
            **kwargs,
        )


class SessionCleanupError(SessionError):
    """Session cleanup error."""

    def __init__(self, message: str, backend: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_cleanup_error", backend=backend, **kwargs)


class SessionMigrationError(SessionError):
    """Session migration error."""

    def __init__(
        self, message: str, from_backend: str | None = None, to_backend: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message,
            error_code="session_migration_error",
            from_backend=from_backend,
            to_backend=to_backend,
            **kwargs,
        )


class SessionEncryptionError(SessionError):
    """Session encryption error."""

    def __init__(self, message: str, session_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_encryption_error", session_id=session_id, **kwargs)


class SessionDecryptionError(SessionError):
    """Session decryption error."""

    def __init__(self, message: str, session_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_decryption_error", session_id=session_id, **kwargs)


class SessionCompressionError(SessionError):
    """Session compression error."""

    def __init__(self, message: str, session_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_compression_error", session_id=session_id, **kwargs)


class SessionDecompressionError(SessionError):
    """Session decompression error."""

    def __init__(self, message: str, session_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="session_decompression_error", session_id=session_id, **kwargs)
