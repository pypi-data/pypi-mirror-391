from _typeshed import Incomplete
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form as Form
from fastapi.security.base import SecurityBase
from starlette.requests import Request as Request
from typing import Any
from typing_extensions import Annotated

class OAuth2PasswordRequestForm:
    grant_type: Incomplete
    username: Incomplete
    password: Incomplete
    scopes: Incomplete
    client_id: Incomplete
    client_secret: Incomplete
    def __init__(self, *, grant_type: Annotated[str | None, None, None] = None, username: Annotated[str, None, None], password: Annotated[str, None, None], scope: Annotated[str, None, None] = '', client_id: Annotated[str | None, None, None] = None, client_secret: Annotated[str | None, None, None] = None) -> None: ...

class OAuth2PasswordRequestFormStrict(OAuth2PasswordRequestForm):
    def __init__(self, grant_type: Annotated[str, None, None], username: Annotated[str, None, None], password: Annotated[str, None, None], scope: Annotated[str, None, None] = '', client_id: Annotated[str | None, None, None] = None, client_secret: Annotated[str | None, None, None] = None) -> None: ...

class OAuth2(SecurityBase):
    model: Incomplete
    scheme_name: Incomplete
    auto_error: Incomplete
    def __init__(self, *, flows: Annotated[OAuthFlowsModel | dict[str, dict[str, Any]], None] = ..., scheme_name: Annotated[str | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...

class OAuth2PasswordBearer(OAuth2):
    def __init__(self, tokenUrl: Annotated[str, None], scheme_name: Annotated[str | None, None] = None, scopes: Annotated[dict[str, str] | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...

class OAuth2AuthorizationCodeBearer(OAuth2):
    def __init__(self, authorizationUrl: str, tokenUrl: Annotated[str, None], refreshUrl: Annotated[str | None, None] = None, scheme_name: Annotated[str | None, None] = None, scopes: Annotated[dict[str, str] | None, None] = None, description: Annotated[str | None, None] = None, auto_error: Annotated[bool, None] = True) -> None: ...
    async def __call__(self, request: Request) -> str | None: ...

class SecurityScopes:
    scopes: Annotated[list[str], None]
    scope_str: Annotated[str, None]
    def __init__(self, scopes: Annotated[list[str] | None, None] = None) -> None: ...
