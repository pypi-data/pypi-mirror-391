import logging
from .constants import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from _typeshed import Incomplete

class Logger(logging.Logger):
    def trace(self, msg, *args, **kwargs) -> None: ...

logger: Incomplete

def get_logger(name: str) -> Logger: ...
