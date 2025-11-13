from _typeshed import Incomplete
from collections.abc import Mapping, Sequence
from pydantic import BaseModel as BaseModel
from typing import Any
from zephyr.exceptions import BaseZephyrException as BaseZephyrException

class HTTPException(BaseZephyrException):
    status_code: Incomplete
    detail: Incomplete
    headers: Incomplete
    def __init__(self, status_code: int, detail: str | None = None, headers: Mapping[str, str] | None = None) -> None: ...

class WebSocketException(BaseZephyrException):
    code: Incomplete
    reason: Incomplete
    def __init__(self, code: int, reason: str | None = None) -> None: ...

RequestErrorModel: type[BaseModel]
WebSocketErrorModel: type[BaseModel]

class ValidationException(BaseZephyrException):
    def __init__(self, errors: Sequence[Any]) -> None: ...
    def errors(self) -> Sequence[Any]: ...

class RequestValidationError(ValidationException):
    body: Incomplete
    def __init__(self, errors: Sequence[Any], *, body: Any = None) -> None: ...

class WebSocketRequestValidationError(ValidationException): ...

class ResponseValidationError(ValidationException):
    body: Incomplete
    def __init__(self, errors: Sequence[Any], *, body: Any = None) -> None: ...

class NoMatchFound(BaseZephyrException):
    def __init__(self, name: str, path_params: dict[str, Any]) -> None: ...
