import datetime
from ._compat import PYDANTIC_V2 as PYDANTIC_V2, UndefinedType as UndefinedType, Url as Url
from _typeshed import Incomplete
from decimal import Decimal
from typing import Any, Callable
from typing_extensions import Annotated
from zephyr._types import IncEx as IncEx

def isoformat(o: datetime.date | datetime.time) -> str: ...
def decimal_encoder(dec_value: Decimal) -> int | float: ...

ENCODERS_BY_TYPE: dict[type[Any], Callable[[Any], Any]]

def generate_encoders_by_class_tuples(type_encoder_map: dict[Any, Callable[[Any], Any]]) -> dict[Callable[[Any], Any], tuple[Any, ...]]: ...

encoders_by_class_tuples: Incomplete

def jsonable_encoder(obj: Annotated[Any, None], include: Annotated[IncEx | None, None] = None, exclude: Annotated[IncEx | None, None] = None, by_alias: Annotated[bool, None] = True, exclude_unset: Annotated[bool, None] = False, exclude_defaults: Annotated[bool, None] = False, exclude_none: Annotated[bool, None] = False, custom_encoder: Annotated[dict[Any, Callable[[Any], Any]] | None, None] = None, sqlalchemy_safe: Annotated[bool, None] = True) -> Any: ...
