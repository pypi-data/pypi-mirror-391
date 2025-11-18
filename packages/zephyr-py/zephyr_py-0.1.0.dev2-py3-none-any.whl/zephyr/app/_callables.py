"""Utilities for handling sync and async callables."""

import asyncio
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


async def run_callable(func: "Callable[..., typing.Any]", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
    """Run a function (sync or async) and return the result.

    Automatically detects if the function is async or sync and runs it appropriately.
    Sync functions are run in a threadpool to avoid blocking.

    Args:
        func: The callable to run (sync or async)
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value from the function

    Example:
        ```python
        # Works with async functions
        result = await run_callable(async_func, arg1, arg2)

        # Works with sync functions
        result = await run_callable(sync_func, arg1, arg2)
        ```
    """
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        from zephyr.app.concurrency import run_in_threadpool

        return await run_in_threadpool(func, *args, **kwargs)


def is_coroutine_callable(func: typing.Any) -> bool:
    """Check if a callable is a coroutine function.

    Args:
        func: The callable to check

    Returns:
        True if the callable is async, False otherwise
    """
    return asyncio.iscoroutinefunction(func)
