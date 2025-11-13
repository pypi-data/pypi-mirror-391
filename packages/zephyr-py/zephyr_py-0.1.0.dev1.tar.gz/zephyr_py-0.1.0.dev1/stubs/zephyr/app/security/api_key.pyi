from _typeshed import Incomplete
from fastapi.openapi.models import APIKey
from fastapi.security.base import SecurityBase
from starlette.requests import Request as Request
from typing_extensions import Annotated

class APIKeyBase(SecurityBase):
    @staticmethod
    def check_api_key(api_key: str | None, auto_error: bool) -> str | None: ...

class APIKeyQuery(APIKeyBase):
    model: APIKey
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, name: Annotated[str, None], scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...

class APIKeyHeader(APIKeyBase):
    model: APIKey
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, name: Annotated[str, None], scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...

class APIKeyCookie(APIKeyBase):
    model: APIKey
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, name: Annotated[str, None], scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...
