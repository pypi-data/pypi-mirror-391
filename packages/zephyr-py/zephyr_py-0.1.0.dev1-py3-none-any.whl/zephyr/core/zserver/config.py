import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Literal
from collections.abc import Callable, Awaitable

from zephyr.core.logging import TRACE_LOG_LEVEL, LOG_LEVELS, get_logger

ASGIApplication = list


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "zephyr.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "zephyr.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "zephyr": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "zephyr.error": {"level": "INFO"},
        "zephyr.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}


class ServerConfig:
    def __init__(
        self,
        app: ASGIApplication | Callable[..., Any] | str,
        host: str = "127.0.0.1",
        port: int = 8000,
        uds: str | None = None,
        fd: int | None = None,
        ws_max_size: int = 16 * 1024 * 1024,
        ws_max_queue: int = 32,
        ws_ping_interval: float | None = 20.0,
        ws_ping_timeout: float | None = 20.0,
        ws_per_message_deflate: bool = True,
        env_file: str | os.PathLike[str] | None = None,
        log_config: dict[str, Any] | str | None = LOGGING_CONFIG,
        log_level: str | int | None = None,
        access_log: bool = True,
        use_colors: bool | None = None,
        reload: bool = False,
        reload_dirs: list[str] | str | None = None,
        reload_delay: float = 0.25,
        reload_includes: list[str] | str | None = None,
        reload_excludes: list[str] | str | None = None,
        workers: int | None = None,
        proxy_headers: bool = True,
        server_header: bool = True,
        date_header: bool = True,
        forwarded_allow_ips: list[str] | str | None = None,
        root_path: str = "",
        limit_concurrency: int | None = None,
        limit_max_requests: int | None = None,
        backlog: int = 2048,
        timeout_keep_alive: int = 5,
        timeout_notify: int = 30,
        timeout_graceful_shutdown: int | None = None,
        callback_notify: Callable[..., Awaitable[None]] | None = None,
        headers: list[tuple[str, str]] | None = None,
        factory: bool = False,
        h11_max_incomplete_event_size: int | None = None,
    ):
        self.app = app
        self.host = host
        self.port = port
        self.uds = uds
        self.fd = fd

        self.ws_max_size = ws_max_size
        self.ws_max_queue = ws_max_queue
        self.ws_ping_interval = ws_ping_interval
        self.ws_ping_timeout = ws_ping_timeout
        self.ws_per_message_deflate = ws_per_message_deflate

        self.log_config = log_config
        self.log_level = log_level
        self.access_log = access_log
        self.use_colors = use_colors

        self.reload = reload
        self.reload_delay = reload_delay
        self.workers = workers or 1
        self.proxy_headers = proxy_headers
        self.server_header = server_header
        self.date_header = date_header
        self.root_path = root_path
        self.limit_concurrency = limit_concurrency
        self.limit_max_requests = limit_max_requests
        self.backlog = backlog
        self.timeout_keep_alive = timeout_keep_alive
        self.timeout_notify = timeout_notify
        self.timeout_graceful_shutdown = timeout_graceful_shutdown
        self.callback_notify = callback_notify

        self.headers: list[tuple[str, str]] = headers or []
        self.encoded_headers: list[tuple[bytes, bytes]] = []
        self.factory = factory
        self.h11_max_incomplete_event_size = h11_max_incomplete_event_size

        self.loaded = False
        self.configure_logging()

        self.reload_dirs: list[Path] = []
        self.reload_dirs_excludes: list[Path] = []
        self.reload_includes: list[str] = []
        self.reload_excludes: list[str] = []

        self.use_subprocess = False

        self.logger = get_logger("ServerConfig")

        if (reload_dirs or reload_includes or reload_excludes) and not self.should_reload:
            self.logger.warning(
                "Current configuration will not reload as not all conditions are met, please refer to documentation."
            )

        # if self.should_reload:
        #     reload_dirs = _normalize_dirs(reload_dirs)
        #     reload_includes = _normalize_dirs(reload_includes)
        #     reload_excludes = _normalize_dirs(reload_excludes)
        #
        #     self.reload_includes, self.reload_dirs = resolve_reload_patterns(reload_includes, reload_dirs)
        #
        #     self.reload_excludes, self.reload_dirs_excludes = resolve_reload_patterns(reload_excludes, [])
        #
        #     reload_dirs_tmp = self.reload_dirs.copy()
        #
        #     for directory in self.reload_dirs_excludes:
        #         for reload_directory in reload_dirs_tmp:
        #             if directory == reload_directory or directory in reload_directory.parents:
        #                 try:
        #                     self.reload_dirs.remove(reload_directory)
        #                 except ValueError:  # pragma: full coverage
        #                     pass
        #
        #     for pattern in self.reload_excludes:
        #         if pattern in self.reload_includes:
        #             self.reload_includes.remove(pattern)  # pragma: full coverage
        #
        #     if not self.reload_dirs:
        #         if reload_dirs:
        #             logging.warning(
        #                 "Provided reload directories %s did not contain valid "
        #                 + "directories, watching current working directory.",
        #                 reload_dirs,
        #             )
        #         self.reload_dirs = [Path(os.getcwd())]
        #
        #     logging.info(
        #         "Will watch for changes in these directories: %s",
        #         sorted(list(map(str, self.reload_dirs))),
        #     )

        if env_file is not None:
            from dotenv import load_dotenv

            self.logger.info("Loading environment from '%s'", env_file)
            load_dotenv(dotenv_path=env_file)

        if workers is None and "WEB_CONCURRENCY" in os.environ:
            self.workers = int(os.environ["WEB_CONCURRENCY"])

        self.forwarded_allow_ips: list[str] | str
        if forwarded_allow_ips is None:
            self.forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
        else:
            self.forwarded_allow_ips = forwarded_allow_ips  # pragma: full coverage

        if self.reload and self.workers > 1:
            self.logger.warning('"workers" flag is ignored when reloading is enabled.')

    @property
    def asgi_version(self) -> Literal["2.0", "3.0"]:
        mapping: dict[str, Literal["2.0", "3.0"]] = {
            "asgi2": "2.0",
            "asgi3": "3.0",
            "wsgi": "3.0",
        }
        return mapping["asgi3"]

    def configure_logging(self) -> None:
        logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")

        if self.log_config is not None:
            if isinstance(self.log_config, dict):
                if self.use_colors in (True, False):
                    self.log_config["formatters"]["default"]["use_colors"] = self.use_colors
                    self.log_config["formatters"]["access"]["use_colors"] = self.use_colors
                logging.config.dictConfig(self.log_config)
            elif isinstance(self.log_config, str) and self.log_config.endswith(".json"):
                with open(self.log_config) as file:
                    loaded_config = json.load(file)
                    logging.config.dictConfig(loaded_config)
            elif isinstance(self.log_config, str) and self.log_config.endswith((".yaml", ".yml")):
                # Install the PyYAML package or the zephyr[standard] optional
                # dependencies to enable this functionality.
                import yaml

                with open(self.log_config) as file:
                    loaded_config = yaml.safe_load(file)
                    logging.config.dictConfig(loaded_config)
            else:
                # See the note about fileConfig() here:
                # https://docs.python.org/3/library/logging.config.html#configuration-file-format
                logging.config.fileConfig(self.log_config, disable_existing_loggers=False)

        if self.log_level is not None:
            if isinstance(self.log_level, str):
                log_level = LOG_LEVELS[self.log_level]
            else:
                log_level = self.log_level
            logging.getLogger("zephyr.error").setLevel(log_level)
            logging.getLogger("zephyr.access").setLevel(log_level)
            logging.getLogger("zephyr.asgi").setLevel(log_level)
        if self.access_log is False:
            logging.getLogger("zephyr.access").handlers = []
            logging.getLogger("zephyr.access").propagate = False

    def load(self) -> None:
        assert not self.loaded

        encoded_headers = [(key.lower().encode("latin1"), value.encode("latin1")) for key, value in self.headers]
        self.encoded_headers = (
            [(b"server", b"Zephyr")] + encoded_headers
            if b"server" not in dict(encoded_headers) and self.server_header
            else encoded_headers
        )

        # if isinstance(self.http, str):
        #     http_protocol_class = import_from_string(HTTP_PROTOCOLS[self.http])
        #     self.http_protocol_class: type[asyncio.Protocol] = http_protocol_class
        # else:
        #     self.http_protocol_class = self.http
        #
        # if isinstance(self.ws, str):
        #     ws_protocol_class = import_from_string(WS_PROTOCOLS[self.ws])
        #     self.ws_protocol_class: type[asyncio.Protocol] | None = ws_protocol_class
        # else:
        #     self.ws_protocol_class = self.ws
        #
        # self.lifespan_class = import_from_string(LIFESPAN[self.lifespan])
        #
        # try:
        #     self.loaded_app = import_from_string(self.app)
        # except ImportFromStringError as exc:
        #     self.logger.error("Error loading ASGI app. %s" % exc)
        #     sys.exit(1)
        #
        # try:
        #     self.loaded_app = self.loaded_app()
        # except TypeError as exc:
        #     if self.factory:
        #         self.logger.error("Error loading ASGI app factory: %s", exc)
        #         sys.exit(1)
        # else:
        #     if not self.factory:
        #         self.logger.warning(
        #             "ASGI app factory detected. Using it, but please consider setting the --factory flag explicitly."
        #         )
        #
        # if self.interface == "auto":
        #     if inspect.isclass(self.loaded_app):
        #         use_asgi_3 = hasattr(self.loaded_app, "__await__")
        #     elif inspect.isfunction(self.loaded_app):
        #         use_asgi_3 = asyncio.iscoroutinefunction(self.loaded_app)
        #     else:
        #         call = getattr(self.loaded_app, "__call__", None)
        #         use_asgi_3 = asyncio.iscoroutinefunction(call)
        #     self.interface = "asgi3" if use_asgi_3 else "asgi2"
        #
        # if self.interface == "wsgi":
        #     self.loaded_app = WSGIMiddleware(self.loaded_app)
        #     self.ws_protocol_class = None
        # elif self.interface == "asgi2":
        #     self.loaded_app = ASGI2Middleware(self.loaded_app)
        #
        # if self.logger.getEffectiveLevel() <= TRACE_LOG_LEVEL:
        #     self.loaded_app = MessageLoggerMiddleware(self.loaded_app)
        # if self.proxy_headers:
        #     self.loaded_app = ProxyHeadersMiddleware(self.loaded_app, trusted_hosts=self.forwarded_allow_ips)

        self.loaded = True

    def setup_event_loop(self) -> None:
        from zephyr.core.loops import uvloop_setup

        uvloop_setup(use_subprocess=self.use_subprocess)


if __name__ == "__main__":
    cfg = ServerConfig("")

    print(cfg.logger)
    print(cfg)
