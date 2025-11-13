from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Callable

import sys
import typing
from contextlib import contextmanager

from pydantic import ConfigDict, PydanticSchemaGenerationError
from pydantic.fields import FieldInfo
from pydantic.v1.typing import evaluate_forwardref
from pydantic_core import PydanticUndefined, PydanticUndefinedType
from zephyr._types import Scope

import zephyr
from zephyr.app._compat import ModelField
from zephyr.app.datastructures import DefaultPlaceholder, DefaultType

if typing.TYPE_CHECKING:
    from zephyr.app.routing import Route

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeGuard
else:  # pragma: no cover
    from typing_extensions import TypeGuard

has_exceptiongroups = True
if sys.version_info < (3, 11):  # pragma: no cover
    try:
        from exceptiongroup import BaseExceptionGroup  # type: ignore[unused-ignore,import-not-found]
    except ImportError:
        has_exceptiongroups = False

T = typing.TypeVar("T")
AwaitableCallable = typing.Callable[..., typing.Awaitable[T]]


@typing.overload
def is_async_callable(obj: AwaitableCallable[T]) -> TypeGuard[AwaitableCallable[T]]: ...


@typing.overload
def is_async_callable(obj: typing.Any) -> TypeGuard[AwaitableCallable[typing.Any]]: ...


def is_async_callable(obj: typing.Any) -> typing.Any:
    while isinstance(obj, functools.partial):
        obj = obj.func

    return inspect.iscoroutinefunction(obj) or (callable(obj) and inspect.iscoroutinefunction(obj.__call__))


T_co = typing.TypeVar("T_co", covariant=True)


class AwaitableOrContextManager(typing.Awaitable[T_co], typing.AsyncContextManager[T_co], typing.Protocol[T_co]): ...


class SupportsAsyncClose(typing.Protocol):
    async def close(self) -> None: ...  # pragma: no cover


SupportsAsyncCloseType = typing.TypeVar("SupportsAsyncCloseType", bound=SupportsAsyncClose, covariant=False)


class AwaitableOrContextManagerWrapper(typing.Generic[SupportsAsyncCloseType]):
    __slots__ = ("aw", "entered")

    def __init__(self, aw: typing.Awaitable[SupportsAsyncCloseType]) -> None:
        self.aw = aw

    def __await__(self) -> typing.Generator[typing.Any, None, SupportsAsyncCloseType]:
        return self.aw.__await__()

    async def __aenter__(self) -> SupportsAsyncCloseType:
        self.entered = await self.aw
        return self.entered

    async def __aexit__(self, *args: typing.Any) -> None | bool:
        await self.entered.close()
        return None


@contextmanager
def collapse_excgroups() -> typing.Generator[None, None, None]:
    try:
        yield
    except BaseException as exc:
        if has_exceptiongroups:  # pragma: no cover
            while isinstance(exc, BaseExceptionGroup) and len(exc.exceptions) == 1:
                exc = exc.exceptions[0]

        raise exc


def get_route_path(scope: Scope) -> str:
    path: str = scope["path"]
    root_path = scope.get("root_path", "")
    if not root_path:
        return path

    if not path.startswith(root_path):
        return path

    if path == root_path:
        return ""

    if path[len(root_path)] == "/":
        return path[len(root_path) :]

    return path


def generate_unique_id(route: Route) -> str:
    operation_id = f"{route.name}{route.path_format}"
    operation_id = re.sub(r"\W", "_", operation_id)
    assert route.methods
    operation_id = f"{operation_id}_{list(route.methods)[0].lower()}"
    return operation_id


def get_value_or_default(
    first_item: DefaultPlaceholder | DefaultType,
    *extra_items: DefaultPlaceholder | DefaultType,
) -> DefaultPlaceholder | DefaultType:
    """
    Pass items or `DefaultPlaceholder`s by descending priority.

    The first one to _not_ be a `DefaultPlaceholder` will be returned.

    Otherwise, the first item (a `DefaultPlaceholder`) will be returned.
    """
    items = (first_item,) + extra_items
    for item in items:
        if not isinstance(item, DefaultPlaceholder):
            return item
    return first_item


def get_typed_annotation(annotation: typing.Any, globalns: dict[str, typing.Any]) -> typing.Any:
    if isinstance(annotation, str):
        annotation = typing.ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


def get_typed_return_annotation(call: Callable[..., typing.Any]) -> typing.Any:
    signature = inspect.signature(call)
    annotation = signature.return_annotation

    if annotation is inspect.Signature.empty:
        return None

    globalns = getattr(call, "__globals__", {})
    return get_typed_annotation(annotation, globalns)


def get_name(endpoint: typing.Callable[..., typing.Any]) -> str:
    return getattr(endpoint, "__name__", endpoint.__class__.__name__)


def is_body_allowed_for_status_code(status_code: int | str | None) -> bool:
    if status_code is None:
        return True
    # Ref: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#patterned-fields-1
    if status_code in {
        "default",
        "1XX",
        "2XX",
        "3XX",
        "4XX",
        "5XX",
    }:
        return True
    current_status_code = int(status_code)
    return not (current_status_code < 200 or current_status_code in {204, 205, 304})


def get_path_param_names(path: str) -> set[str]:
    return set(re.findall("{(.*?)}", path))


def create_model_field(
    name: str,
    type_: typing.Any,
    class_validators: dict[str, typing.Any] | None = None,
    default: typing.Any | None = PydanticUndefined,
    field_info: FieldInfo | None = None,
    alias: str | None = None,
    mode: typing.Literal["validation", "serialization"] = "validation",
) -> ModelField:
    field_info = field_info or FieldInfo(annotation=type_, default=default, alias=alias)
    kwargs = {"name": name, "field_info": field_info}
    kwargs.update({"mode": mode})
    try:
        return ModelField(**kwargs)  # type: ignore[arg-type]
    except (RuntimeError, PydanticSchemaGenerationError):
        raise zephyr.exceptions.BaseZephyrException(
            "Invalid args for response field! Hint: "
            f"check that {type_} is a valid Pydantic field type. "
            "If you are using a return type annotation that is not a valid Pydantic "
            "field (e.g. Union[Response, dict, None]) you can disable generating the "
            "response model from the type annotation with the path operation decorator "
            "parameter response_model=None. Read more: "
            "https://fastapi.tiangolo.com/tutorial/response-model/"
        ) from None
