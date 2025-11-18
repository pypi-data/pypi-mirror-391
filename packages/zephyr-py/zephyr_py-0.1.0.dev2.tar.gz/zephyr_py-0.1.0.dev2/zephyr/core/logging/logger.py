import logging

from .constants import TRACE_LOG_LEVEL


class Logger(logging.Logger):
    def __str__(self):
        return f"<ZEPHYRLogger <{super().__str__()}>"

    def trace(self, msg, *args, **kwargs):
        self.log(TRACE_LOG_LEVEL, msg, *args, **kwargs)


logging._loggerClass = Logger

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=TRACE_LOG_LEVEL,  # Set the minimum logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str) -> Logger:
    return logging.getLogger(name)
