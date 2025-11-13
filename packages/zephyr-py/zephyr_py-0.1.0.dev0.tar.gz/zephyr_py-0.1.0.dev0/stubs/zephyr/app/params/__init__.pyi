from .body import Body as Body, File as File, Form as Form
from .param import Cookie as Cookie, Header as Header, Param as Param, ParamTypes as ParamTypes, Path as Path, Query as Query
from _typeshed import Incomplete
from collections.abc import Callable, Sequence
from typing import Any

__all__ = ['Header', 'Path', 'Query', 'Cookie', 'Body', 'Form', 'Param', 'ParamTypes', 'File', 'Security', 'Depends']

class Depends:
    dependency: Incomplete
    use_cache: Incomplete
    def __init__(self, dependency: Callable[..., Any] | None = None, *, use_cache: bool = True) -> None: ...

class Security(Depends):
    scopes: Incomplete
    def __init__(self, dependency: Callable[..., Any] | None = None, *, scopes: Sequence[str] | None = None, use_cache: bool = True) -> None: ...
