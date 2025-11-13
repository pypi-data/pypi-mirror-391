from __future__ import annotations

import asyncio
import dataclasses
import email
import functools
import json
import re
import traceback
from collections.abc import Sequence, Callable, Awaitable, Coroutine, AsyncIterator, Mapping
from contextlib import asynccontextmanager, AsyncExitStack
from enum import IntEnum, Enum
from typing import Any, TypeVar, Annotated, Type, Pattern

from pydantic import BaseModel
from pydantic._internal._utils import lenient_issubclass
from pydantic_core.core_schema import ModelField
from typing_extensions import Doc

from zephyr import BaseZephyrException
from zephyr._types import ASGIApp, Scope, Receive, Send, DecoratedCallable, IncEx, AppType
from zephyr.app import params
from zephyr.app._compat import _normalize_errors, _get_model_config, _model_dump, Undefined
from zephyr.app._exception_handler import wrap_app_handling_exceptions
from zephyr.app._utils import (
    generate_unique_id,
    get_value_or_default,
    get_name,
    get_typed_return_annotation,
    is_body_allowed_for_status_code,
    create_model_field,
    is_async_callable,
    get_route_path,
)
from zephyr.app.concurrency import run_in_threadpool
from zephyr.app.convertors import Convertor, CONVERTOR_TYPES
from zephyr.app.datastructures import Default, DefaultPlaceholder, URLPath
from zephyr.app.dependencies.models import Dependant
from zephyr.app.dependencies.utils import (
    get_body_field,
    get_dependant,
    get_parameterless_sub_dependant,
    get_flat_dependant,
    _should_embed_body_fields,
    solve_dependencies,
)
from zephyr.app.encoders import jsonable_encoder
from zephyr.app.exceptions import HTTPException, ResponseValidationError, RequestValidationError, NoMatchFound
from zephyr.app.middleware import Middleware
from zephyr.app.requests import Request
from zephyr.app.responses import PlainTextResponse, Response, JSONResponse
from zephyr.core.zserver.lifespan import Lifespan


_T = TypeVar("_T")


class Match(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


def replace_params(
    path: str,
    param_convertors: dict[str, Convertor[Any]],
    path_params: dict[str, str],
) -> tuple[str, dict[str, str]]:
    for key, value in list(path_params.items()):
        if "{" + key + "}" in path:
            convertor = param_convertors[key]
            value = convertor.to_string(value)
            path = path.replace("{" + key + "}", value)
            path_params.pop(key)
    return path, path_params


def _prepare_response_content(
    res: Any,
    *,
    exclude_unset: bool,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
) -> Any:
    if isinstance(res, BaseModel):
        read_with_orm_mode = getattr(_get_model_config(res), "read_with_orm_mode", None)
        if read_with_orm_mode:
            # Let from_orm extract the data from this model instead of converting
            # it now to a dict.
            # Otherwise, there's no way to extract lazy data that requires attribute
            # access instead of dict iteration, e.g. lazy relationships.
            return res
        return _model_dump(
            res,
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    elif isinstance(res, list):
        return [
            _prepare_response_content(
                item,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
            for item in res
        ]
    elif isinstance(res, dict):
        return {
            k: _prepare_response_content(
                v,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
            for k, v in res.items()
        }
    elif dataclasses.is_dataclass(res):
        return dataclasses.asdict(res)
    return res


def _merge_lifespan_context(original_context: Lifespan[Any], nested_context: Lifespan[Any]) -> Lifespan[Any]:
    @asynccontextmanager
    async def merged_lifespan(
        app: AppType,
    ) -> AsyncIterator[Mapping[str, Any] | None]:
        async with original_context(app) as maybe_original_state:
            async with nested_context(app) as maybe_nested_state:
                if maybe_nested_state is None and maybe_original_state is None:
                    yield None  # old ASGI compatibility
                else:
                    yield {**(maybe_nested_state or {}), **(maybe_original_state or {})}

    return merged_lifespan  # type: ignore[return-value]


async def serialize_response(
    *,
    field: ModelField | None = None,
    response_content: Any,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    is_coroutine: bool = True,
) -> Any:
    if field:
        errors = []
        if not hasattr(field, "serialize"):
            # pydantic v1
            response_content = _prepare_response_content(
                response_content,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
        if is_coroutine:
            value, errors_ = field.validate(response_content, {}, loc=("response",))
        else:
            value, errors_ = await run_in_threadpool(field.validate, response_content, {}, loc=("response",))
        if isinstance(errors_, list):
            errors.extend(errors_)
        elif errors_:
            errors.append(errors_)
        if errors:
            raise ResponseValidationError(errors=_normalize_errors(errors), body=response_content)

        if hasattr(field, "serialize"):
            return field.serialize(
                value,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )

        return jsonable_encoder(
            value,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    else:
        return jsonable_encoder(response_content)


async def run_endpoint_function(*, dependant: Dependant, values: dict[str, Any], is_coroutine: bool) -> Any:
    # Only called by get_request_handler. Has been split into its own function to
    # facilitate profiling endpoints, since inner functions are harder to profile.
    assert dependant.call is not None, "dependant.call must be a function"

    if is_coroutine:
        return await dependant.call(**values)
    else:
        return await run_in_threadpool(dependant.call, **values)


def get_request_handler(
    dependant: Dependant,
    body_field: ModelField | None = None,
    status_code: int | None = None,
    response_class: Type[Response] | DefaultPlaceholder = Default(JSONResponse),
    response_field: ModelField | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    dependency_overrides_provider: Any | None = None,
    embed_body_fields: bool = False,
) -> Callable[[Request], Coroutine[Any, Any, Response]]:
    assert dependant.call is not None, "dependant.call must be a function"
    is_coroutine = asyncio.iscoroutinefunction(dependant.call)
    is_body_form = body_field and isinstance(body_field.field_info, params.Form)
    if isinstance(response_class, DefaultPlaceholder):
        actual_response_class: Type[Response] = response_class.value
    else:
        actual_response_class = response_class

    async def app(request: Request) -> Response:
        response: Response | None = None
        async with AsyncExitStack() as file_stack:
            try:
                body: Any = None
                if body_field:
                    if is_body_form:
                        body = await request.form()
                        file_stack.push_async_callback(body.close)
                    else:
                        body_bytes = await request.body()
                        if body_bytes:
                            json_body: Any = Undefined
                            content_type_value = request.headers.get("content-type")
                            if not content_type_value:
                                json_body = await request.json()
                            else:
                                message = email.message.Message()
                                message["content-type"] = content_type_value
                                if message.get_content_maintype() == "application":
                                    subtype = message.get_content_subtype()
                                    if subtype == "json" or subtype.endswith("+json"):
                                        json_body = await request.json()
                            if json_body != Undefined:
                                body = json_body
                            else:
                                body = body_bytes
            except json.JSONDecodeError as e:
                validation_error = RequestValidationError(
                    [
                        {
                            "type": "json_invalid",
                            "loc": ("body", e.pos),
                            "msg": "JSON decode error",
                            "input": {},
                            "ctx": {"error": e.msg},
                        }
                    ],
                    body=e.doc,
                )
                raise validation_error from e
            except HTTPException:
                # If a middleware raises an HTTPException, it should be raised again
                raise
            except Exception as e:
                http_error = HTTPException(status_code=400, detail="There was an error parsing the body")
                raise http_error from e
            errors: list[Any] = []
            async with AsyncExitStack() as async_exit_stack:
                solved_result = await solve_dependencies(
                    request=request,
                    dependant=dependant,
                    body=body,
                    dependency_overrides_provider=dependency_overrides_provider,
                    async_exit_stack=async_exit_stack,
                    embed_body_fields=embed_body_fields,
                )
                errors = solved_result.errors
                if not errors:
                    raw_response = await run_endpoint_function(
                        dependant=dependant,
                        values=solved_result.values,
                        is_coroutine=is_coroutine,
                    )
                    if isinstance(raw_response, Response):
                        if raw_response.background is None:
                            raw_response.background = solved_result.background_tasks
                        response = raw_response
                    else:
                        response_args: dict[str, Any] = {"background": solved_result.background_tasks}
                        # If status_code was set, use it, otherwise use the default from the
                        # response class, in the case of redirect it's 307
                        current_status_code = status_code if status_code else solved_result.response.status_code
                        if current_status_code is not None:
                            response_args["status_code"] = current_status_code
                        if solved_result.response.status_code:
                            response_args["status_code"] = solved_result.response.status_code
                        content = await serialize_response(
                            field=response_field,
                            response_content=raw_response,
                            include=response_model_include,
                            exclude=response_model_exclude,
                            by_alias=response_model_by_alias,
                            exclude_unset=response_model_exclude_unset,
                            exclude_defaults=response_model_exclude_defaults,
                            exclude_none=response_model_exclude_none,
                            is_coroutine=is_coroutine,
                        )
                        response = actual_response_class(content, **response_args)
                        if not is_body_allowed_for_status_code(response.status_code):
                            response.body = b""
                        response.headers.raw.extend(solved_result.response.headers.raw)
            if errors:
                validation_error = RequestValidationError(_normalize_errors(errors), body=body)
                raise validation_error
        if response is None:
            raise BaseZephyrException(
                "No response object was returned. There's a high chance that the "
                "application code is raising an exception and a dependency with yield "
                "has a block with a bare except, or a block with except Exception, "
                "and is not raising the exception again. Read more about it in the "
            )
        return response

    return app


def request_response(
    func: Callable[[Request], Awaitable[Response] | Response],
) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    f: Callable[[Request], Awaitable[Response]] = (
        func if is_async_callable(func) else functools.partial(run_in_threadpool, func)
    )

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            response = await f(request)
            await response(scope, receive, send)

        await wrap_app_handling_exceptions(app, request)(scope, receive, send)

    return app


class _DefaultLifespan:
    def __init__(self, router: Router):
        self._router = router

    async def __aenter__(self) -> None:
        await self._router.startup()

    async def __aexit__(self, *exc_info: object) -> None:
        await self._router.shutdown()

    def __call__(self: _T, app: object) -> _T:
        return self


PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(
    path: str,
) -> tuple[Pattern[str], str, dict[str, Convertor[Any]]]:
    """
    Given a path string, like: "/{username:str}",
    or a host string, like: "{subdomain}.mydomain.org", return a three-tuple
    of (regex, format, {param_name:convertor}).

    regex:      "/(?P<username>[^/]+)"
    format:     "/{username}"
    convertors: {"username": StringConvertor()}
    """
    is_host = not path.startswith("/")

    path_regex = "^"
    path_format = ""
    duplicated_params = set()

    idx = 0
    param_convertors = {}
    for match in PARAM_REGEX.finditer(path):
        param_name, convertor_type = match.groups("str")
        convertor_type = convertor_type.lstrip(":")
        assert convertor_type in CONVERTOR_TYPES, f"Unknown path convertor '{convertor_type}'"
        convertor = CONVERTOR_TYPES[convertor_type]

        path_regex += re.escape(path[idx : match.start()])
        path_regex += f"(?P<{param_name}>{convertor.regex})"

        path_format += path[idx : match.start()]
        path_format += "{%s}" % param_name

        if param_name in param_convertors:
            duplicated_params.add(param_name)

        param_convertors[param_name] = convertor

        idx = match.end()

    if duplicated_params:
        names = ", ".join(sorted(duplicated_params))
        ending = "s" if len(duplicated_params) > 1 else ""
        raise ValueError(f"Duplicated param name{ending} {names} at path {path}")

    if is_host:
        # Align with `Host.matches()` behavior, which ignores port.
        hostname = path[idx:].split(":")[0]
        path_regex += re.escape(hostname) + "$"
    else:
        path_regex += re.escape(path[idx:]) + "$"

    path_format += path[idx:]

    return re.compile(path_regex), path_format, param_convertors


class BaseRoute:
    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        raise NotImplementedError()  # pragma: no cover

    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        raise NotImplementedError()  # pragma: no cover

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError()  # pragma: no cover

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        A route may be used in isolation as a stand-alone ASGI app.
        This is a somewhat contrived case, as they'll almost always be used
        within a Router, but could be useful for some tooling and minimal apps.
        """
        match, child_scope = self.matches(scope)
        if match == Match.NONE:
            if scope["type"] == "http":
                response = PlainTextResponse("Not Found", status_code=404)
                await response(scope, receive, send)
            elif scope["type"] == "websocket":  # pragma: no branch
                websocket_close = WebSocketClose()
                await websocket_close(scope, receive, send)
            return

        scope.update(child_scope)
        await self.handle(scope, receive, send)


class Route(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[[Request], Awaitable[Response] | Response],
        *,
        response_model: Any = Default(None),
        status_code: int | None = None,
        methods: list[str] | set[str] | None = None,
        operation_id: str | None = None,
        name: str | None = None,
        route_cls_override: Type[Route] | None = None,
        generate_unique_id_fn: Callable[Route, str] | DefaultPlaceholder = Default(generate_unique_id),
        responses: dict[int | str, dict[str, Any]] | None = None,
        response_class: Type[Response] | DefaultPlaceholder = Default(JSONResponse),
    ) -> None:
        self.path = path
        self.endpoint = endpoint

        if isinstance(response_model, DefaultPlaceholder):
            return_annotation = get_typed_return_annotation(endpoint)
            if lenient_issubclass(return_annotation, Response):
                response_model = None
            else:
                response_model = return_annotation
        self.response_model = response_model
        self.response_class = response_class
        self.responses = responses or {}
        self.operation_id = operation_id
        self.generate_unique_id_fn = generate_unique_id_fn
        self.name = get_name(endpoint) if name is None else name
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)
        if methods is None:
            methods = ["GET"]
        self.methods: set[str] = {method.upper() for method in methods}
        if isinstance(generate_unique_id_fn, DefaultPlaceholder):
            current_generate_unique_id: Callable[[Route], str] = generate_unique_id_fn.value
        else:
            current_generate_unique_id = generate_unique_id_fn
        self.unique_id = self.operation_id or current_generate_unique_id(self)
        # normalize enums e.g. http.HTTPStatus
        if isinstance(status_code, IntEnum):
            status_code = int(status_code)
        self.status_code = status_code
        if self.response_model:
            assert is_body_allowed_for_status_code(status_code), (
                f"Status code {status_code} must not have a response body"
            )
            response_name = "Response_" + self.unique_id
            self.response_field = create_model_field(
                name=response_name,
                type_=self.response_model,
                mode="serialization",
            )
        else:
            self.response_field = None  # type: ignore
            self.secure_cloned_response_field = None

        response_fields = {}
        for additional_status_code, response in self.responses.items():
            assert isinstance(response, dict), "An additional response must be a dict"
            model = response.get("model")
            if model:
                assert is_body_allowed_for_status_code(additional_status_code), (
                    f"Status code {additional_status_code} must not have a response body"
                )
                response_name = f"Response_{additional_status_code}_{self.unique_id}"
                response_field = create_model_field(name=response_name, type_=model, mode="serialization")
                response_fields[additional_status_code] = response_field
        if response_fields:
            self.response_fields: dict[int | str, ModelField] = response_fields
        else:
            self.response_fields = {}

        assert callable(endpoint), "An endpoint must be a callable"

        self.dependencies = []

        self.dependant = get_dependant(path=self.path_format, call=self.endpoint)
        for depends in self.dependencies[::-1]:
            self.dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=self.path_format),
            )

        self._flat_dependant = get_flat_dependant(self.dependant)
        self._embed_body_fields = _should_embed_body_fields(self._flat_dependant.body_params)

        self.body_field = get_body_field(
            flat_dependant=self._flat_dependant,
            name=self.unique_id,
            embed_body_fields=self._embed_body_fields,
        )
        self.app = request_response(self.get_route_handler())

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        return get_request_handler(
            dependant=self.dependant,
            body_field=self.body_field,
            status_code=self.status_code,
            response_class=self.response_class,
            response_field=self.secure_cloned_response_field,
            embed_body_fields=self._embed_body_fields,
        )

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        match, child_scope = self._matches(scope)
        if match != Match.NONE:
            child_scope["route"] = self
        return match, child_scope

    def _matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, Any]
        if scope["type"] == "http":
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {"endpoint": self.endpoint, "path_params": path_params}
                if self.methods and scope["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}

    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        seen_params = set(path_params.keys())
        expected_params = set(self.param_convertors.keys())

        if name != self.name or seen_params != expected_params:
            raise NoMatchFound(name, path_params)

        path, remaining_params = replace_params(self.path_format, self.param_convertors, path_params)
        assert not remaining_params
        return URLPath(path=path, protocol="http")

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.methods and scope["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if "app" in scope:
                raise HTTPException(status_code=405, headers=headers)
            else:
                response = PlainTextResponse("Method Not Allowed", status_code=405, headers=headers)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Route)
            and self.path == other.path
            and self.endpoint == other.endpoint
            and self.methods == other.methods
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        methods = sorted(self.methods or [])
        path, name = self.path, self.name
        return f"{class_name}(path={path!r}, name={name!r}, methods={methods!r})"


class Router:
    def __init__(
        self,
        routes: Sequence[BaseRoute] | None = None,
        default: ASGIApp | None = None,
        lifespan: Lifespan[Any] | None = None,
        *,
        middlewares: Sequence[Middleware] | None = None,
        prefix: Annotated[str, Doc("Optional Path prefix for the Router.")] = "",
        # default_resp_class=Annotated[Type[Response], JSONResponse],
        # resopnses: Annotated[dict[int | str, dict[str, Any]] | None, Doc("Additional Resp!!")] = None,
        # callbacks: Annotated[
        #     list[BaseRoute] | None,
        #     Doc("""OpenAPI callbacks that should apply to all *path operations* in this router."""),
        # ],
        generate_unique_id_fn: Annotated[
            Callable[[Route], str],
            Doc(
                """
                Customize the function used to generate unique IDs for the *path
                operations* shown in the generated OpenAPI.

                This is particularly useful when automatically generating clients or
                SDKs for your API.

                Read more about it in the
                [FastAPI docs about how to Generate Clients](https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function).
                """
            ),
        ] = Default(generate_unique_id),
        redirect_slashes: Annotated[bool, Doc("Whether to redirect slashes")] = True,
    ) -> None:
        if prefix:
            assert prefix.startswith("/"), "A path prefix must start with '/'"
            assert not prefix.endswith("/"), "A path prefix must not end with '/'"

        self.prefix = prefix
        self.routes = routes or []
        self.default = default or self.not_found

        self.route_class = Route

        self.redirect_slashes = redirect_slashes

        self.lifespan_context = lifespan or _DefaultLifespan(self)
        self.generate_unique_id_function = generate_unique_id_fn

        self.middleware_stack = self.app

        for cls, args, kwargs in reversed(middlewares or []):
            self.middleware_stack = cls(self.middleware_stack, *args, **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        The main entry point to the Router class.
        """
        await self.middleware_stack(scope, receive, send)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Router) and self.routes == other.routes

    async def lifespan(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle ASGI lifespan messages, which allows us to manage application
        startup and shutdown events.
        """
        started = False
        app: Any = scope.get("app")
        await receive()
        try:
            async with self.lifespan_context(app) as maybe_state:
                if maybe_state is not None:
                    if "state" not in scope:
                        raise RuntimeError('The server does not support "state" in the lifespan scope.')
                    scope["state"].update(maybe_state)
                await send({"type": "lifespan.startup.complete"})
                started = True
                await receive()
        except BaseException:
            exc_text = traceback.format_exc()
            if started:
                await send({"type": "lifespan.shutdown.failed", "message": exc_text})
            else:
                await send({"type": "lifespan.startup.failed", "message": exc_text})
            raise
        else:
            await send({"type": "lifespan.shutdown.complete"})

    def route(
        self,
        path: str,
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_route(
                path,
                func,
                methods=methods,
                name=name,
                include_in_schema=include_in_schema,
            )
            return func

        return decorator

    async def app(self, scope: Scope, receive: Receive, send: Send) -> None:
        if "route" not in scope:
            scope["router"] = self

        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
            return

        partial = None

        for route in self.routes:
            # Determine if any route matches the incoming scope,
            # and hand over to the matching route if found.
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                scope.update(child_scope)
                await route.handle(scope, receive, send)
                return
            elif match == Match.PARTIAL and partial is None:
                partial = route
                partial_scope = child_scope

        if partial is not None:
            #  Handle partial matches. These are cases where an endpoint is
            # able to handle the request, but is not a preferred option.
            # We use this in particular to deal with "405 Method Not Allowed".
            scope.update(partial_scope)
            await partial.handle(scope, receive, send)
            return

        route_path = get_route_path(scope)
        if scope["type"] == "http" and self.redirect_slashes and route_path != "/":
            redirect_scope = dict(scope)
            if route_path.endswith("/"):
                redirect_scope["path"] = redirect_scope["path"].rstrip("/")
            else:
                redirect_scope["path"] = redirect_scope["path"] + "/"

            for route in self.routes:
                match, child_scope = route.matches(redirect_scope)
                if match != Match.NONE:
                    redirect_url = URL(scope=redirect_scope)
                    response = RedirectResponse(url=str(redirect_url))
                    await response(scope, receive, send)
                    return

        await self.default(scope, receive, send)

    def add_route(
        self,
        path: str,
        endpoint: Callable[[Request], Awaitable[Response] | Response],
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
    ) -> None:  # pragma: no cover
        route = Route(
            path,
            endpoint=endpoint,
            methods=methods,
            name=name,
        )
        self.routes.append(route)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[[Request], Awaitable[Response] | Response],
        *,
        response_model: Any = Default(None),
        status_code: int | None = None,
        methods: list[str] | set[str] | None = None,
        operation_id: str | None = None,
        name: str | None = None,
        route_cls_override: Type[Route] | None = None,
        generate_unique_id_fn: Callable[Route, str] | DefaultPlaceholder = Default(generate_unique_id),
    ):
        route_cls = route_cls_override or self.route_class

        current_generate_unique_id = get_value_or_default(generate_unique_id_fn, self.generate_unique_id_function)

        route = route_cls(
            self.prefix + path,
            endpoint=endpoint,
            response_model=response_model,
            status_code=status_code,
            methods=methods,
            operation_id=operation_id,
            name=name,
            generate_unique_id_fn=current_generate_unique_id,
        )

        self.routes.append(route)

    def api_route(
        self,
        path: str,
        *,
        response_model: Any = Default(None),
        status_code: int | None = None,
        methods: list[str] | set[str] | None = None,
        operation_id: str | None = None,
        name: str | None = None,
        generate_unique_id_fn: Callable[Route, str] | DefaultPlaceholder = Default(generate_unique_id),
    ):
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_route(
                path,
                func,
                response_model=response_model,
                status_code=status_code,
                methods=methods,
                operation_id=operation_id,
                name=name,
                generate_unique_id_fn=generate_unique_id_fn,
            )
            return func

        return decorator

    def get(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.api_route(
            path=path,
            status_code=status_code,
            methods=["GET"],
        )

    def put(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.api_route(
            path=path,
            status_code=status_code,
            methods=["PUT"],
        )

    def post(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.api_route(
            path=path,
            status_code=status_code,
            methods=["POST"],
        )

    def delete(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.api_route(
            path=path,
            status_code=status_code,
            methods=["DELETE"],
        )

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    @staticmethod
    async def not_found(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            websocket_close = WebSocketClose()
            await websocket_close(scope, receive, send)
            return

        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        # if "app" in scope:
        #     raise HTTPException(status_code=404)
        # else:
        response = PlainTextResponse("Not Found", status_code=404)
        await response(scope, receive, send)
