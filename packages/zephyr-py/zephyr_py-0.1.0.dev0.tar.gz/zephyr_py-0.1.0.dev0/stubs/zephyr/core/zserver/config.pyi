import os
from _typeshed import Incomplete
from collections.abc import Awaitable, Callable as Callable
from pathlib import Path
from typing import Any, Literal
from zephyr.core.logging import LOG_LEVELS as LOG_LEVELS, TRACE_LOG_LEVEL as TRACE_LOG_LEVEL, get_logger as get_logger

ASGIApplication = list
LOGGING_CONFIG: dict[str, Any]

class ServerConfig:
    app: Incomplete
    host: Incomplete
    port: Incomplete
    uds: Incomplete
    fd: Incomplete
    ws_max_size: Incomplete
    ws_max_queue: Incomplete
    ws_ping_interval: Incomplete
    ws_ping_timeout: Incomplete
    ws_per_message_deflate: Incomplete
    log_config: Incomplete
    log_level: Incomplete
    access_log: Incomplete
    use_colors: Incomplete
    reload: Incomplete
    reload_delay: Incomplete
    workers: Incomplete
    proxy_headers: Incomplete
    server_header: Incomplete
    date_header: Incomplete
    root_path: Incomplete
    limit_concurrency: Incomplete
    limit_max_requests: Incomplete
    backlog: Incomplete
    timeout_keep_alive: Incomplete
    timeout_notify: Incomplete
    timeout_graceful_shutdown: Incomplete
    callback_notify: Incomplete
    headers: list[tuple[str, str]]
    encoded_headers: list[tuple[bytes, bytes]]
    factory: Incomplete
    h11_max_incomplete_event_size: Incomplete
    loaded: bool
    reload_dirs: list[Path]
    reload_dirs_excludes: list[Path]
    reload_includes: list[str]
    reload_excludes: list[str]
    use_subprocess: bool
    logger: Incomplete
    forwarded_allow_ips: list[str] | str
    def __init__(self, app: ASGIApplication | Callable[..., Any] | str, host: str = '127.0.0.1', port: int = 8000, uds: str | None = None, fd: int | None = None, ws_max_size: int = ..., ws_max_queue: int = 32, ws_ping_interval: float | None = 20.0, ws_ping_timeout: float | None = 20.0, ws_per_message_deflate: bool = True, env_file: str | os.PathLike[str] | None = None, log_config: dict[str, Any] | str | None = ..., log_level: str | int | None = None, access_log: bool = True, use_colors: bool | None = None, reload: bool = False, reload_dirs: list[str] | str | None = None, reload_delay: float = 0.25, reload_includes: list[str] | str | None = None, reload_excludes: list[str] | str | None = None, workers: int | None = None, proxy_headers: bool = True, server_header: bool = True, date_header: bool = True, forwarded_allow_ips: list[str] | str | None = None, root_path: str = '', limit_concurrency: int | None = None, limit_max_requests: int | None = None, backlog: int = 2048, timeout_keep_alive: int = 5, timeout_notify: int = 30, timeout_graceful_shutdown: int | None = None, callback_notify: Callable[..., Awaitable[None]] | None = None, headers: list[tuple[str, str]] | None = None, factory: bool = False, h11_max_incomplete_event_size: int | None = None) -> None: ...
    @property
    def asgi_version(self) -> Literal['2.0', '3.0']: ...
    def configure_logging(self) -> None: ...
    def load(self) -> None: ...
    def setup_event_loop(self) -> None: ...
