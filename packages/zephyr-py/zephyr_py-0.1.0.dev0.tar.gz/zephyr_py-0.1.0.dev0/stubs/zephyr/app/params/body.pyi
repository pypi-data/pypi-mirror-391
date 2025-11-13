from .._compat import PYDANTIC_VERSION_MINOR_TUPLE as PYDANTIC_VERSION_MINOR_TUPLE, Undefined as Undefined
from _typeshed import Incomplete
from pydantic import AnyUrl as AnyUrl
from pydantic.fields import FieldInfo
from typing import Any, Callable
from typing_extensions import TypedDict, deprecated

class Example(TypedDict, total=False):
    summary: str | None
    description: str | None
    value: Any | None
    externalValue: AnyUrl | None
    __pydantic_config__: Incomplete

class Body(FieldInfo):
    embed: Incomplete
    media_type: Incomplete
    include_in_schema: Incomplete
    openapi_examples: Incomplete
    deprecated: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., embed: bool | None = None, annotation: Any | None = None, media_type: str = 'application/json', alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class Form(Body):
    def __init__(self, default: Any = ..., *, media_type: str = 'application/x-www-form-urlencoded', default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class File(Form):
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, media_type: str = 'multipart/form-data', alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...
