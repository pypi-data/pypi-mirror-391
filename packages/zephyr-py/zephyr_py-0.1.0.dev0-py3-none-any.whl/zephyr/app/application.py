import typing
from collections.abc import Callable

# Use built-in typing for Python 3.11+
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

# Create simple Doc and deprecated functions if not available
try:
    from typing_extensions import Doc, deprecated
except ImportError:

    def Doc(text: str) -> str:
        return text

    def deprecated(text: str) -> str:
        return text


from zephyr._types import AppType, Lifespan, ASGIApp, Scope, Receive, Send
from zephyr.app import routing
from zephyr.app._utils import generate_unique_id
from zephyr.app.datastructures import Default, State
from zephyr.app.middleware import Middleware
from zephyr.app.requests import Request
from zephyr.app.responses import Response
from zephyr.app.routing import BaseRoute
from zephyr.core.logging import get_logger
from zephyr.conf import settings


class Zephyr:
    def __init__(
        self: AppType,
        *,
        debug: bool | None = None,
        routes: Annotated[
            list[BaseRoute] | None,
            Doc(
                """
                         **Note**: you probably shouldn't use this parameter, it is inherited
                         from Starlette and supported for compatibility.

                         ---

                         A list of routes to serve incoming HTTP and WebSocket requests.
                         """
            ),
            deprecated(
                """
                         You normally wouldn't use this parameter with FastAPI, it is inherited
                         from Starlette and supported for compatibility.

                         In FastAPI, you normally would use the *path operation methods*,
                         like `app.get()`, `app.post()`, etc.
                         """
            ),
        ] = None,
        title: Annotated[
            str,
            Doc(
                """
                         The title of the API.

                         It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                         Read more in the
                         [FastAPI docs for Metadata and Docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-api).

                         **Example**

                         ```python
                         from fastapi import FastAPI

                         app = FastAPI(title="ChimichangApp")
                         ```
                         """
            ),
        ] = "Zephyr",
        version: str = "1.0.0",
        description: str | None = None,
        root_path: str = "",
        lifespan: Annotated[
            Lifespan[AppType] | None,
            Doc(
                """
                    A `Lifespan` context manager handler. This replaces `startup` and
                    `shutdown` functions with a single context manager.

                    Read more in the
                    [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).
                    """
            ),
        ] = None,
        generate_unique_id_function: Annotated[
            Callable[[routing.Route], str],
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
    ):
        self.logger = get_logger("Zephyr")

        # Smart defaults - use settings system for environment-based defaults
        if debug is None:
            debug = settings.get("DEBUG", False)

        self.debug = debug
        self.title = title
        self.version = version
        self.description = description
        self.root_path = root_path

        self.router: routing.Router = routing.Router(
            routes=routes,
            lifespan=lifespan,
            generate_unique_id_fn=generate_unique_id_function,
        )

        self.state = State()
        self.exception_handlers = {}
        self.user_middleware = []
        self.middleware_stack: ASGIApp | None = None

        # Auto-enable middleware based on configuration
        self._setup_default_middleware()

    def _setup_default_middleware(self):
        """Setup middleware by reading settings directly."""
        if settings.get("ENABLE_REQUEST_ID", True):
            self._add_request_id_middleware()

        # if settings.get("ENABLE_CORS", False):
        #     cors_origins = settings.get("CORS_ORIGINS", ["*"] if self.debug else [])
        #     cors_methods = settings.get("CORS_ALLOW_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        #     cors_headers = settings.get("CORS_ALLOW_HEADERS", ["*"])
        #     cors_credentials = settings.get("CORS_ALLOW_CREDENTIALS", False)

        #     self.use_cors(
        #         allow_origins=cors_origins,
        #         allow_methods=cors_methods,
        #         allow_headers=cors_headers,
        #         allow_credentials=cors_credentials,
        #     )

        if settings.get("ENABLE_RATE_LIMITING", True):
            self._add_rate_limiting_middleware()

        if settings.get("ENABLE_COMPRESSION", True):
            self._add_compression_middleware()

        if settings.get("ENABLE_CACHING", True):
            self._add_caching_middleware()

        if settings.get("ENABLE_METRICS", True):
            self._add_metrics_middleware()

        if settings.get("ENABLE_TRACING", True):
            self._add_tracing_middleware()

        if settings.get("ENABLE_HEALTH_CHECKS", True):
            self._setup_health_endpoints()

        if settings.get("ENABLE_AUTO_DOCS", True):
            self._setup_docs_endpoints()

    def _add_request_id_middleware(self):
        """Add request ID middleware"""
        from zephyr.app.middleware.request_id import RequestIDMiddleware

        self.add_middleware(RequestIDMiddleware)

    def _add_rate_limiting_middleware(self):
        """Add rate limiting middleware"""
        from zephyr.app.middleware.rate_limit import RateLimitMiddleware

        requests = settings.get("RATE_LIMIT_REQUESTS", 1000)
        window = settings.get("RATE_LIMIT_WINDOW", 60)

        self.add_middleware(RateLimitMiddleware, requests=requests, window=window)

    def _add_compression_middleware(self):
        """Add compression middleware"""
        from zephyr.app.middleware.compression import CompressionMiddleware

        self.add_middleware(CompressionMiddleware)

    def _add_caching_middleware(self):
        """Add caching middleware"""
        from zephyr.app.middleware.cache import CacheMiddleware

        self.add_middleware(CacheMiddleware)

    def _add_metrics_middleware(self):
        """Add metrics middleware"""
        from zephyr.app.middleware.metrics import MetricsMiddleware

        self.add_middleware(MetricsMiddleware)

    def _add_tracing_middleware(self):
        """Add tracing middleware"""
        from zephyr.app.middleware.tracing import TracingMiddleware

        self.add_middleware(TracingMiddleware)

    def _setup_health_endpoints(self):
        """Setup health check endpoints"""
        from zephyr.app.responses import JSONResponse

        @self.get("/health")
        async def health():
            return JSONResponse(
                {
                    "status": "healthy",
                    "version": self.version,
                    "uptime_seconds": 0,  # Will be calculated by health middleware
                }
            )

        @self.get("/health/ready")
        async def readiness():
            return JSONResponse({"status": "ready"})

        @self.get("/health/live")
        async def liveness():
            return JSONResponse({"status": "alive"})

    def _setup_docs_endpoints(self):
        """Setup documentation endpoints"""
        from zephyr.app.responses import JSONResponse

        @self.get("/openapi.json")
        async def openapi():
            # TODO: Generate OpenAPI schema
            return JSONResponse(
                {
                    "openapi": "3.1.0",
                    "info": {"title": self.title, "version": self.version, "description": self.description},
                    "paths": {},
                }
            )

    def build_middleware_stack(self) -> ASGIApp:
        debug = self.debug
        error_handler = None
        exception_handlers: dict[typing.Any, typing.Callable[[Request, Exception], Response]] = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = (
            # [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
            # +
            self.user_middleware
            # + [Middleware(ExceptionMiddleware, handlers=exception_handlers, debug=debug)]
        )

        app = self.router
        for cls, args, kwargs in reversed(middleware):
            app = cls(app, *args, **kwargs)
        return app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.root_path:
            scope["root_path"] = self.root_path
        scope["app"] = self
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)

    def get(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.router.get(
            path=path,
            status_code=status_code,
        )

    def put(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.router.put(
            path=path,
            status_code=status_code,
        )

    def post(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.router.post(
            path=path,
            status_code=status_code,
        )

    def delete(
        self,
        path: str,
        *,
        status_code: int | None = None,
    ):
        return self.router.delete(
            path=path,
            status_code=status_code,
        )

    def middleware(self, middleware_class, *args, **kwargs):
        """Decorator to add middleware to the application"""

        def decorator(func):
            self.user_middleware.append(Middleware(middleware_class, *args, **kwargs))
            return func

        return decorator

    def add_middleware(self, middleware_class, *args, **kwargs):
        """Add middleware to the application"""
        self.user_middleware.append(Middleware(middleware_class, *args, **kwargs))
        return self

    def use_cors(self, **kwargs):
        """Add CORS middleware with default settings"""
        from zephyr.app.middleware.cors import CORSMiddleware

        self.add_middleware(CORSMiddleware, **kwargs)
        return self
