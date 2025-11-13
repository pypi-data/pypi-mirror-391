from _typeshed import Incomplete
from fastapi.security.base import SecurityBase
from starlette.requests import Request as Request
from typing_extensions import Annotated

class OpenIdConnect(SecurityBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, openIdConnectUrl: Annotated[str, None], scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...
