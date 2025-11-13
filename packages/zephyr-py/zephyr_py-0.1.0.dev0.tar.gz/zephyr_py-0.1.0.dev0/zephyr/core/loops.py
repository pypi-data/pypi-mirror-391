import asyncio
import sys

try:
    import uvloop

    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False


def uvloop_setup(use_subprocess: bool = False) -> None:
    """Setup event loop policy with uvloop if available, otherwise use default asyncio."""
    if UVLOOP_AVAILABLE and sys.platform != "win32":
        # Use uvloop on Unix-like systems for better performance
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    else:
        # Use default asyncio policy (Windows compatible)
        if hasattr(asyncio, "WindowsProactorEventLoopPolicy") and sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        else:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
