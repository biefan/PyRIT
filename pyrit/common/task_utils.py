# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio
from collections.abc import Awaitable, Iterable
from typing import TypeVar

TaskResultT = TypeVar("TaskResultT")


async def gather_with_cleanup_async(tasks: Iterable[Awaitable[TaskResultT]]) -> list[TaskResultT]:
    """
    Gather ordered results, cancelling and draining siblings on failure or cancellation.

    Caller cancellation during the drain is delivered only after every child has finished
    cleanup. A child's cleanup error must not replace the original failure.

    Returns:
        list[TaskResultT]: Results in input order.
    """
    scheduled_tasks = [asyncio.ensure_future(task) for task in tasks]
    try:
        return await asyncio.gather(*scheduled_tasks)
    except BaseException:
        for task in scheduled_tasks:
            if not task.done():
                task.cancel()
        drain = asyncio.gather(*scheduled_tasks, return_exceptions=True)
        outer_cancellation: asyncio.CancelledError | None = None
        while not drain.done():
            try:
                await asyncio.shield(drain)
            except asyncio.CancelledError as cancellation:
                outer_cancellation = cancellation
        drain.result()
        if outer_cancellation:
            raise outer_cancellation from None
        raise
