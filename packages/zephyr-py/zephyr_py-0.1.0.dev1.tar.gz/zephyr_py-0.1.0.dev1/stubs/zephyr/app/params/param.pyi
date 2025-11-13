from _typeshed import Incomplete
from collections.abc import Callable as Callable
from enum import Enum
from pydantic import AnyUrl as AnyUrl
from pydantic.fields import FieldInfo
from typing import Any, TypedDict
from typing_extensions import deprecated
from zephyr.app._compat import Undefined as Undefined

class Example(TypedDict, total=False):
    summary: str | None
    description: str | None
    value: Any | None
    externalValue: AnyUrl | None
    __pydantic_config__: Incomplete

class ParamTypes(Enum):
    query = 'query'
    header = 'header'
    path = 'path'
    cookie = 'cookie'

class Param(FieldInfo):
    in_: ParamTypes
    example: Incomplete
    include_in_schema: Incomplete
    openapi_examples: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class Path(Param):
    in_: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class Query(Param):
    in_: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class Header(Param):
    in_: Incomplete
    convert_underscores: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, convert_underscores: bool = True, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...

class Cookie(Param):
    in_: Incomplete
    def __init__(self, default: Any = ..., *, default_factory: Callable | Any | None = ..., annotation: Any | None = None, alias: str | None = None, alias_priority: int | None = ..., validation_alias: str | None = None, serialization_alias: str | None = None, title: str | None = None, description: str | None = None, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, discriminator: str | None = None, strict: bool | None = ..., multiple_of: float | None = ..., allow_inf_nan: bool | None = ..., max_digits: int | None = ..., decimal_places: int | None = ..., examples: list | None | Any = None, openapi_examples: dict[str, Example] | None = None, deprecated: deprecated | str | bool | None = None, include_in_schema: bool = True, json_schema_extra: dict[str, Any] | None = None, **extra: Any) -> None: ...
