from collections.abc import Callable, Sequence
from typing import Any

from .body import Body, Form, File
from .param import Param, ParamTypes, Cookie, Header, Path, Query


class Depends:
    def __init__(self, dependency: Callable[..., Any] | None = None, *, use_cache: bool = True):
        self.dependency = dependency
        self.use_cache = use_cache

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        cache = "" if self.use_cache else ", use_cache=False"
        return f"{self.__class__.__name__}({attr}{cache})"


class Security(Depends):
    def __init__(
        self,
        dependency: Callable[..., Any] | None = None,
        *,
        scopes: Sequence[str] | None = None,
        use_cache: bool = True,
    ):
        super().__init__(dependency=dependency, use_cache=use_cache)
        self.scopes = scopes or []


__all__ = ["Header", "Path", "Query", "Cookie", "Body", "Form", "Param", "ParamTypes", "File", "Security", "Depends"]
