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
from zephyr.app._callables import run_callable
from zephyr.app._utils import generate_unique_id
from zephyr.app.datastructures import Default, State
from zephyr.app.middleware import Middleware
from zephyr.app.requests import Request
from zephyr.app.responses import Response
from zephyr.app.routing import BaseRoute
from zephyr.core.logging import get_logger
from zephyr.conf import settings


class Zephyr:
    """Zephyr ASGI web framework application."""

    HOOKS: list[str] = ["after_startup", "before_shutdown"]

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
        # Smart defaults - use settings system for environment-based defaults
        if debug is None:
            debug = settings.get("DEBUG", False)

        self.debug = debug
        self.title = title
        self.version = version
        self.description = description
        self.root_path = root_path

        # Initialize logger with app title
        self.logger = get_logger(title or "Zephyr")

        self.router: routing.Router = routing.Router(
            routes=routes,
            lifespan=lifespan,
            generate_unique_id_fn=generate_unique_id_function,
        )

        self.state = State()
        self.exception_handlers = {}
        self.user_middleware = []
        self.middleware_stack: ASGIApp | None = None

        # Server instances for run/serve methods
        self._server = None
        self._server_config = None

        # Hook system
        self._hooks: dict[str, Callable] = {}
        self.logger.debug("Zephyr app initialized: %s v%s", self.title, self.version)

        # Dependency overrides for testing
        self.dependency_overrides: dict[Callable, Callable] = {}

        # Auto-enable middleware based on configuration
        self._setup_default_middleware()

    def _setup_default_middleware(self):
        """Setup middleware by reading settings directly."""
        # Add WebSocket CSP headers middleware first
        if settings.get("ENABLE_WEBSOCKET_SUPPORT", True):
            self.logger.debug("Adding WebSocket CSP middleware")
            self._add_websocket_csp_middleware()
            self.logger.debug("WebSocket CSP middleware added")

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

    def _add_websocket_csp_middleware(self):
        """Add WebSocket CSP headers middleware to allow browser WebSocket connections."""
        from zephyr.app.middleware.websocket import WebSocketCSPMiddleware

        self.add_middleware(WebSocketCSPMiddleware)

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

        # Inject exception handlers into scope for exception middleware
        exception_handlers = {}
        status_handlers = {}
        for key, value in self.exception_handlers.items():
            if isinstance(key, int):
                status_handlers[key] = value
            else:
                exception_handlers[key] = value
        scope["zephyr.exception_handlers"] = (exception_handlers, status_handlers)

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

    def websocket(self, path: str, name: str | None = None):
        """
        Decorator to register a WebSocket endpoint.

        Args:
            path: The URL path
            name: Optional name for the route

        Example:
            ```python
            @app.websocket("/ws")
            async def websocket_endpoint(websocket):
                await websocket.accept()
                try:
                    while True:
                        data = await websocket.receive_text()
                        await websocket.send_text(f"Echo: {data}")
                except WebSocketDisconnect:
                    pass
            ```
        """

        def decorator(func: Callable) -> Callable:
            # Import WebSocket route handling
            from zephyr.app.websockets import WebSocket
            from zephyr.app.routing import WebSocketRoute

            # Wrap the function to inject WebSocket instance
            async def websocket_wrapper(scope, receive, send):
                self.logger.info("WebSocket endpoint called for path: %s", scope.get("path"))
                websocket = WebSocket(scope, receive, send)
                await func(websocket)

            # Add as a WebSocket route
            route = WebSocketRoute(
                path=path,
                endpoint=websocket_wrapper,
                name=name,
            )
            self.router.routes.append(route)
            self.logger.debug("WebSocket route registered: %s -> %s (route: %s)", path, func.__name__, route)
            return func

        return decorator

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

    # ========== Server Run Methods ==========

    def configure_server(self, **kwargs):
        """Configure the server with given options."""
        from zephyr.core.zserver.config import ServerConfig
        from zephyr.core.zserver.server import Server

        if self._server_config is None:
            self._server_config = ServerConfig(app=self, **kwargs)
            self._server = Server(self._server_config)
        return self._server

    @property
    def server(self):
        """Get the server instance, creating it if necessary."""
        if self._server is None:
            self.configure_server()
        return self._server

    def run(self, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None:
        """
        Run the application server (blocking, synchronous entry point).

        This is the main entry point for running your Zephyr application.
        It handles asyncio setup automatically, so you don't need to use asyncio.run().

        Args:
            host: Host to bind to (default: "127.0.0.1")
            port: Port to bind to (default: 8000)
            **kwargs: Additional server configuration options

        Example:
            ```python
            from zephyr import Zephyr

            app = Zephyr()

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            # Simply call run() - no asyncio needed!
            app.run(host="0.0.0.0", port=8000)
            ```
        """
        server = self._server or self.configure_server(host=host, port=port, **kwargs)
        server.config.host = host
        server.config.port = port
        server.run()

    async def serve(self, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None:
        """
        Serve the application (async entry point for embedding in existing event loops).

        Use this when you need to run the server inside an existing asyncio event loop,
        such as in tests or when orchestrating multiple async services.

        Args:
            host: Host to bind to (default: "127.0.0.1")
            port: Port to bind to (default: 8000)
            **kwargs: Additional server configuration options

        Example:
            ```python
            import asyncio
            from zephyr import Zephyr

            app = Zephyr()

            async def main():
                await app.serve(host="0.0.0.0", port=8000)

            asyncio.run(main())
            ```
        """
        server = self._server or self.configure_server(host=host, port=port, **kwargs)
        server.config.host = host
        server.config.port = port
        await server.serve()

    # ========== Hook System ==========

    def register_hook(self, hook_name: str):
        """
        Decorator to register lifecycle hooks.

        Args:
            hook_name: Either "after_startup" or "before_shutdown"

        Raises:
            ValueError: If hook_name is invalid

        Example:
            ```python
            @app.register_hook("after_startup")
            async def startup():
                app.logger.info("Application starting up...")

            @app.register_hook("before_shutdown")
            async def shutdown():
                app.logger.info("Application shutting down...")
            ```
        """
        if hook_name not in self.__class__.HOOKS:
            msg = f"Invalid hook {hook_name}. Supported hooks: {self.__class__.HOOKS}"
            raise ValueError(msg)

        def decorator(func: Callable) -> Callable:
            self._hooks[hook_name] = func
            self.logger.debug("Hook registered: %s -> %s", hook_name, func.__name__)
            return func

        return decorator

    async def run_hook(self, hook_name: str) -> None:
        """
        Execute a registered hook by name.

        Args:
            hook_name: Name of the hook to run

        Raises:
            ValueError: If hook_name is invalid

        Example:
            ```python
            await app.run_hook("after_startup")
            ```
        """
        if hook_name not in self.__class__.HOOKS:
            raise ValueError(f"Invalid hook {hook_name}. Supported hooks: {self.__class__.HOOKS}")

        if hook_name not in self._hooks:
            return

        func = self._hooks[hook_name]
        try:
            self.logger.debug("Running hook: %s", hook_name)
            await run_callable(func)
            self.logger.debug("Hook completed: %s", hook_name)
        except Exception as exc:
            self.logger.error(
                "Error in hook %s@%s: %s",
                self.title,
                hook_name,
                exc,
                exc_info=True,
            )
            raise

    async def run_after_startup_hook(self) -> None:
        """Run the after_startup hook."""
        await self.run_hook("after_startup")

    async def run_before_shutdown_hook(self) -> None:
        """Run the before_shutdown hook."""
        await self.run_hook("before_shutdown")

    # Backward compatibility - map old event names to new hooks
    def on_event(self, event_type: str):
        """
        Decorator to register event handlers for startup and shutdown.

        Backward compatibility wrapper. Maps to hooks:
        - "startup" -> "after_startup"
        - "shutdown" -> "before_shutdown"

        Args:
            event_type: Either "startup" or "shutdown"

        Example:
            ```python
            @app.on_event("startup")
            async def startup():
                app.logger.info("Application starting up...")
            ```
        """
        # Map old event names to new hook names
        hook_mapping = {
            "startup": "after_startup",
            "shutdown": "before_shutdown",
        }

        if event_type not in hook_mapping:
            raise ValueError(f"Invalid event type: {event_type}. Must be 'startup' or 'shutdown'")

        hook_name = hook_mapping[event_type]
        return self.register_hook(hook_name)

    def add_event_handler(self, event_type: str, func: Callable) -> None:
        """
        Register an event handler programmatically.

        Backward compatibility wrapper. Maps to hooks:
        - "startup" -> "after_startup"
        - "shutdown" -> "before_shutdown"

        Args:
            event_type: Either "startup" or "shutdown"
            func: The handler function (can be sync or async)

        Example:
            ```python
            async def on_startup():
                app.logger.info("Starting up...")

            app.add_event_handler("startup", on_startup)
            ```
        """
        # Map old event names to new hook names
        hook_mapping = {
            "startup": "after_startup",
            "shutdown": "before_shutdown",
        }

        if event_type not in hook_mapping:
            raise ValueError(f"Invalid event type: {event_type}. Must be 'startup' or 'shutdown'")

        hook_name = hook_mapping[event_type]
        self._hooks[hook_name] = func
        self.logger.debug("Event handler registered: %s -> %s", event_type, func.__name__)

    # ========== Router Composition ==========

    def include_router(
        self,
        router: routing.Router,
        *,
        prefix: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """
        Include another router's routes into this application.

        Args:
            router: The Router instance to include
            prefix: URL prefix to prepend to all routes
            tags: Tags to add to all routes (for OpenAPI)

        Example:
            ```python
            from zephyr import Zephyr
            from zephyr.app.routing import Router

            app = Zephyr()
            api_router = Router()

            @api_router.get("/users")
            async def list_users():
                return {"users": []}

            app.include_router(api_router, prefix="/api/v1")
            # Route will be available at /api/v1/users
            ```
        """
        # Add all routes from the router with the prefix
        for route in router.routes:
            # Clone the route with the new prefix
            if hasattr(route, "path"):
                route_copy = route
                if prefix:
                    # Update the path with prefix
                    original_path = route.path
                    new_path = prefix.rstrip("/") + "/" + original_path.lstrip("/")
                    route.path = new_path
                    # Re-compile the path regex
                    if hasattr(route, "path_regex"):
                        from zephyr.app.routing import compile_path

                        route.path_regex, route.path_format, route.param_convertors = compile_path(new_path)
                self.router.routes.append(route)

    def mount(self, path: str, app: ASGIApp, name: str | None = None) -> None:
        """
        Mount an ASGI application at a specific path.

        Args:
            path: The path to mount at
            app: The ASGI application to mount
            name: Optional name for the mount

        Example:
            ```python
            from zephyr import Zephyr

            app = Zephyr()

            # Mount a static file server or another ASGI app
            app.mount("/static", static_files_app)
            ```
        """
        from zephyr.app.routing import Mount

        mount_route = Mount(path, app, name)
        self.router.routes.append(mount_route)
        self.logger.debug("Mounted ASGI app at %s", path)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable,
        **kwargs,
    ) -> None:
        """
        Add an API route directly (facade to router.add_api_route).

        Args:
            path: The URL path
            endpoint: The endpoint function
            **kwargs: Additional route options

        Example:
            ```python
            async def get_user(user_id: int):
                return {"user_id": user_id}

            app.add_api_route("/users/{user_id}", get_user, methods=["GET"])
            ```
        """
        self.router.add_api_route(path, endpoint, **kwargs)

    # ========== Exception Handlers ==========

    def add_exception_handler(
        self,
        exc_class_or_status_code: int | type[Exception],
        handler: Callable[[Request, Exception], Response],
    ) -> None:
        """
        Register an exception handler.

        Args:
            exc_class_or_status_code: Exception class or HTTP status code
            handler: Handler function that takes (request, exc) and returns Response

        Example:
            ```python
            from zephyr.app.responses import JSONResponse

            async def handle_value_error(request, exc):
                return JSONResponse(
                    {"error": str(exc)},
                    status_code=400
                )

            app.add_exception_handler(ValueError, handle_value_error)
            ```
        """
        self.exception_handlers[exc_class_or_status_code] = handler

    def exception_handler(
        self,
        exc_class_or_status_code: int | type[Exception],
    ):
        """
        Decorator to register an exception handler.

        Args:
            exc_class_or_status_code: Exception class or HTTP status code

        Example:
            ```python
            @app.exception_handler(ValueError)
            async def handle_value_error(request, exc):
                return JSONResponse(
                    {"error": str(exc)},
                    status_code=400
                )
            ```
        """

        def decorator(func: Callable) -> Callable:
            self.add_exception_handler(exc_class_or_status_code, func)
            return func

        return decorator
