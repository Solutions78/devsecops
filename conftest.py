"""Minimal async test support plugin.

This lightweight plugin allows pytest to execute ``async def`` test functions
without depending on the full **pytest-asyncio** package.  It is **not** a
drop-in replacement for every advanced feature of that library, but it is more
than enough for the current test-suite which:

1. Marks coroutine tests with ``@pytest.mark.asyncio``.
2. Requires only a default event-loop to run them.

If an async test is collected this plugin spins up a fresh event-loop, executes
the coroutine, and then closes the loop so resources are released cleanly.
"""

from __future__ import annotations

import asyncio
import inspect
import typing as _t

import pytest


def pytest_configure(config: pytest.Config) -> None:  # noqa: D401
    """Register the ``asyncio`` marker so pytest does not raise warnings."""

    config.addinivalue_line(
        "markers",
        "asyncio: mark a test function as an asyncio coroutine so the built-in"
        " event-loop runner provided by the local ``conftest.py`` executes it.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Item) -> bool | None:  # noqa: D401
    """Intercept function calls and run *coroutine* tests inside an event loop.

    When pytest is about to call a test function, this hook checks whether the
    underlying object is an ``async def`` coroutine. If so, it creates an
    event-loop, executes the coroutine, and returns ``True`` to signal that the
    call has been handled. Non-coroutine tests are left untouched (returning
    ``None`` lets pytest proceed with its default behaviour).
    """

    test_obj = pyfuncitem.obj

    if not inspect.iscoroutinefunction(test_obj):
        # Let pytest handle regular (non-async) test functions.
        return None

    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(test_obj(**pyfuncitem.funcargs))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    # Returning *True* tells pytest that we've already executed the test.
    return True

