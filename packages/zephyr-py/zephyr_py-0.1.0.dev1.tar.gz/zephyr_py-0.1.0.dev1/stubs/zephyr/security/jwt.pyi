from _typeshed import Incomplete
from jose import JWTError
from pydantic import BaseModel
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send

class JWTError(Exception): ...
class JWTExpiredError(JWTError): ...
class JWTInvalidError(JWTError): ...

class JWTConfig(BaseModel):
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    issuer: str | None
    audience: str | None

class JWTPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    jti: str
    type: str
    scope: list[str]
    extra: dict[str, object]

class JWTManager:
    config: Incomplete
    def __init__(self, config: JWTConfig) -> None: ...
    async def create_access_token(self, user_id: str, scope: list[str] | None = None, extra_claims: dict[str, object] | None = None) -> str: ...
    async def create_refresh_token(self, user_id: str) -> str: ...
    async def verify_token(self, token: str, token_type: str = 'access') -> JWTPayload: ...
    async def decode_token(self, token: str, verify: bool = True) -> JWTPayload: ...
    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]: ...
