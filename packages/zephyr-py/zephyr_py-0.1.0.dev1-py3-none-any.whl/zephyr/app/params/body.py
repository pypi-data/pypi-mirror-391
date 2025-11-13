import warnings
from typing import Any, Callable

from pydantic import AnyUrl
from pydantic.fields import FieldInfo
from typing_extensions import deprecated, TypedDict

from .._compat import (
    PYDANTIC_VERSION_MINOR_TUPLE,
    Undefined,
)

_Unset: Any = Undefined


class Example(TypedDict, total=False):
    summary: str | None
    description: str | None
    value: Any | None
    externalValue: AnyUrl | None

    __pydantic_config__ = {"extra": "allow"}


class Body(FieldInfo):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        default_factory: Callable | Any | None = _Unset,
        embed: bool | None = None,
        annotation: Any | None = None,
        media_type: str = "application/json",
        alias: str | None = None,
        alias_priority: int | None = _Unset,
        validation_alias: str | None = None,
        serialization_alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        discriminator: str | None = None,
        strict: bool | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        examples: list | None | Any = None,
        openapi_examples: dict[str, Example] | None = None,
        deprecated: deprecated | str | bool | None = None,
        include_in_schema: bool = True,
        json_schema_extra: dict[str, Any] | None = None,
        **extra: Any,
    ):
        self.embed = embed
        self.media_type = media_type
        self.include_in_schema = include_in_schema
        self.openapi_examples = openapi_examples
        kwargs = dict(
            default=default,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            discriminator=discriminator,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **extra,
        )
        if examples is not None:
            kwargs["examples"] = examples
        current_json_schema_extra = json_schema_extra or extra
        if PYDANTIC_VERSION_MINOR_TUPLE < (2, 7):
            self.deprecated = deprecated
        else:
            kwargs["deprecated"] = deprecated
        kwargs.update(
            {
                "annotation": annotation,
                "alias_priority": alias_priority,
                "validation_alias": validation_alias,
                "serialization_alias": serialization_alias,
                "strict": strict,
                "json_schema_extra": current_json_schema_extra,
            }
        )
        kwargs["pattern"] = pattern

        use_kwargs = {k: v for k, v in kwargs.items() if v is not _Unset}

        super().__init__(**use_kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"


class Form(Body):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        media_type: str = "application/x-www-form-urlencoded",
        default_factory: Callable | Any | None = _Unset,
        annotation: Any | None = None,
        alias: str | None = None,
        alias_priority: int | None = _Unset,
        validation_alias: str | None = None,
        serialization_alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        discriminator: str | None = None,
        strict: bool | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        examples: list | None | Any = None,
        openapi_examples: dict[str, Example] | None = None,
        deprecated: deprecated | str | bool | None = None,
        include_in_schema: bool = True,
        json_schema_extra: dict[str, Any] | None = None,
        **extra: Any,
    ):
        super().__init__(
            default=default,
            default_factory=default_factory,
            annotation=annotation,
            media_type=media_type,
            alias=alias,
            alias_priority=alias_priority,
            validation_alias=validation_alias,
            serialization_alias=serialization_alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            discriminator=discriminator,
            strict=strict,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            max_digits=max_digits,
            decimal_places=decimal_places,
            deprecated=deprecated,
            examples=examples,
            openapi_examples=openapi_examples,
            include_in_schema=include_in_schema,
            json_schema_extra=json_schema_extra,
            **extra,
        )


class File(Form):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        default_factory: Callable | Any | None = _Unset,
        annotation: Any | None = None,
        media_type: str = "multipart/form-data",
        alias: str | None = None,
        alias_priority: int | None = _Unset,
        validation_alias: str | None = None,
        serialization_alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        discriminator: str | None = None,
        strict: bool | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        examples: list | None | Any = None,
        openapi_examples: dict[str, Example] | None = None,
        deprecated: deprecated | str | bool | None = None,
        include_in_schema: bool = True,
        json_schema_extra: dict[str, Any] | None = None,
        **extra: Any,
    ):
        super().__init__(
            default=default,
            default_factory=default_factory,
            annotation=annotation,
            media_type=media_type,
            alias=alias,
            alias_priority=alias_priority,
            validation_alias=validation_alias,
            serialization_alias=serialization_alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            discriminator=discriminator,
            strict=strict,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            max_digits=max_digits,
            decimal_places=decimal_places,
            deprecated=deprecated,
            examples=examples,
            openapi_examples=openapi_examples,
            include_in_schema=include_in_schema,
            json_schema_extra=json_schema_extra,
            **extra,
        )
