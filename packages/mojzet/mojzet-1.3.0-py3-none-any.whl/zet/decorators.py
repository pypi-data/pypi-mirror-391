import asyncio
from collections.abc import Coroutine
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

from aiohttp import ClientSession
from zet.http import make_session

P = ParamSpec("P")
R = TypeVar("R")


def async_command(f: Callable[P, Coroutine[None, None, R]]) -> Callable[P, R]:
    @wraps(f)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        c = f(*args, **kwargs)
        return asyncio.run(c)

    return wrapped


def pass_session(
    f: Callable[Concatenate[ClientSession, P], Coroutine[None, None, R]],
) -> Callable[P, Coroutine[None, None, R]]:
    """Pass the http session as first parameter."""

    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        async with make_session() as session:
            return await f(session, *args, **kwargs)

    return wrapper
