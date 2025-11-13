from __future__ import annotations

import functools
from contextlib import asynccontextmanager

import sys
import typing
import warnings

import anyio.to_thread
from anyio import CapacityLimiter

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

P = ParamSpec("P")
T = typing.TypeVar("T")


async def run_until_first_complete(*args: tuple[typing.Callable, dict]) -> None:  # type: ignore[type-arg]
    warnings.warn(
        "run_until_first_complete is deprecated and will be removed in a future version.",
        DeprecationWarning,
    )

    async with anyio.create_task_group() as task_group:

        async def run(func: typing.Callable[[], typing.Coroutine]) -> None:  # type: ignore[type-arg]
            await func()
            task_group.cancel_scope.cancel()

        for func, kwargs in args:
            task_group.start_soon(run, functools.partial(func, **kwargs))


async def run_in_threadpool(func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    func = functools.partial(func, *args, **kwargs)
    return await anyio.to_thread.run_sync(func)


class _StopIteration(Exception):
    pass


def _next(iterator: typing.Iterator[T]) -> T:
    # We can't raise `StopIteration` from within the threadpool iterator
    # and catch it outside that context, so we coerce them into a different
    # exception type.
    try:
        return next(iterator)
    except StopIteration:
        raise _StopIteration


async def iterate_in_threadpool(
    iterator: typing.Iterable[T],
) -> typing.AsyncIterator[T]:
    as_iterator = iter(iterator)
    while True:
        try:
            yield await anyio.to_thread.run_sync(_next, as_iterator)
        except _StopIteration:
            break


@asynccontextmanager
async def contextmanager_in_threadpool(
    cm: typing.ContextManager[T],
) -> typing.AsyncGenerator[T, None]:
    # blocking __exit__ from running waiting on a free thread
    # can create race conditions/deadlocks if the context manager itself
    # has its own internal pool (e.g. a database connection pool)
    # to avoid this we let __exit__ run without a capacity limit
    # since we're creating a new limiter for each call, any non-zero limit
    # works (1 is arbitrary)
    exit_limiter = CapacityLimiter(1)
    try:
        yield await run_in_threadpool(cm.__enter__)
    except Exception as e:
        ok = bool(await anyio.to_thread.run_sync(cm.__exit__, type(e), e, e.__traceback__, limiter=exit_limiter))
        if not ok:
            raise e
    else:
        await anyio.to_thread.run_sync(cm.__exit__, None, None, None, limiter=exit_limiter)
