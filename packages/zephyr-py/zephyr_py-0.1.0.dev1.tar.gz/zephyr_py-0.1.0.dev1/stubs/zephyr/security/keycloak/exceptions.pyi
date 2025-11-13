from _typeshed import Incomplete
from zephyr.exceptions import BaseZephyrException as BaseZephyrException

class KeycloakError(BaseZephyrException):
    message: Incomplete
    status_code: Incomplete
    def __init__(self, message: str, status_code: int | None = None) -> None: ...

class KeycloakConnectionError(KeycloakError):
    def __init__(self, message: str = 'Failed to connect to Keycloak server') -> None: ...

class KeycloakAuthenticationError(KeycloakError):
    def __init__(self, message: str = 'Authentication failed', status_code: int | None = None) -> None: ...

class KeycloakTokenError(KeycloakError):
    def __init__(self, message: str = 'Token operation failed', status_code: int | None = None) -> None: ...

class KeycloakAdminError(KeycloakError):
    def __init__(self, message: str = 'Admin API operation failed', status_code: int | None = None) -> None: ...

class KeycloakRealmNotFoundError(KeycloakError):
    realm: Incomplete
    def __init__(self, realm: str) -> None: ...

class KeycloakUserNotFoundError(KeycloakError):
    user_id: Incomplete
    def __init__(self, user_id: str) -> None: ...

class KeycloakInvalidTokenError(KeycloakTokenError):
    def __init__(self, message: str = 'Invalid token') -> None: ...

class KeycloakExpiredTokenError(KeycloakTokenError):
    def __init__(self, message: str = 'Token expired') -> None: ...
