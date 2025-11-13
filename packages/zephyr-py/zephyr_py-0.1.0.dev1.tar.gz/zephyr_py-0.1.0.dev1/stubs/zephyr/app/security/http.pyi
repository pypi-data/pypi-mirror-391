from _typeshed import Incomplete
from fastapi.security.base import SecurityBase
from pydantic import BaseModel
from starlette.requests import Request as Request
from typing_extensions import Annotated

class HTTPBasicCredentials(BaseModel):
    username: Annotated[str, None]
    password: Annotated[str, None]

class HTTPAuthorizationCredentials(BaseModel):
    scheme: Annotated[str, None]
    credentials: Annotated[str, None]

class HTTPBase(SecurityBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, scheme: str, scheme_name: str | None = None, description: str | None = None, auto_error: bool = True) -> None: ...
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None: ...

class HTTPBasic(HTTPBase):
    model: Incomplete
    scheme_name: Incomplete
    realm: Incomplete
    auto_error: Incomplete
    def __init__(self, *, scheme_name: Annotated[str | None, None] = None, realm: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> HTTPBasicCredentials | None: ...

class HTTPBearer(HTTPBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, bearerFormat: Annotated[str | None, None] = None, scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None: ...

class HTTPDigest(HTTPBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None: ...
