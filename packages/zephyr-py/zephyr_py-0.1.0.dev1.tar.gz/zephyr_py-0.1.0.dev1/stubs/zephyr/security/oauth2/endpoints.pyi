from .config import OAuth2Config as OAuth2Config
from .exceptions import InvalidRequestError as InvalidRequestError, OAuth2Error as OAuth2Error
from .server import OAuth2Server as OAuth2Server
from _typeshed import Incomplete
from typing import Any
from urllib.parse import urlparse as urlparse

class BaseEndpoint:
    server: Incomplete
    config: Incomplete
    logger: Incomplete
    def __init__(self, server: OAuth2Server) -> None: ...

class AuthorizationEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class TokenEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class RevocationEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class IntrospectionEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class DeviceAuthorizationEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class JWKSEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...

class UserInfoEndpoint(BaseEndpoint):
    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None: ...
