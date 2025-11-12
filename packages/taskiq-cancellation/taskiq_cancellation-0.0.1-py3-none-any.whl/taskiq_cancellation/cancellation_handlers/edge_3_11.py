# FIXME: bunch of issues because of Python 3.11+ exclusivity
#
# Edge cancellation handler is using asyncio.TaskGroup which was introduced in 3.11 and
# uses expect-star syntax that was also introduced in the same version
# - mypy has to ignore this file because it can't finish static parsing
# - ruff's python version has to be set at 3.11+ so it wouldn't complain
#
# I'm not sure how to mitigate these issues. Maybe this can be put in a separate module somehow
# and then integrated? Maybe this can be rewritten to not use TaskGroup (probably easier to do)?

import sys
import logging
import asyncio
from collections.abc import Coroutine
from typing import Callable, TYPE_CHECKING, Generic, Any

if sys.version_info >= (3, 11):
    from typing import ParamSpec, TypeVar
else:
    from typing_extensions import ParamSpec, TypeVar

from taskiq_cancellation.abc.started_listening_event import StartedListeningEvent
from taskiq_cancellation.exceptions import TaskCancellationException
from taskiq_cancellation.utils import StopTaskGroupException

if TYPE_CHECKING:
    from taskiq_cancellation.abc.backend import CancellationBackend


Params = ParamSpec("Params")
Result = TypeVar("Result")


class EdgeCancellationHandler(Generic[Params, Result]):
    """
    Wrapper around a task function that handles cancellation

    Uses edge cancellation provided by asyncio. That means :ref:`asyncio.CancelledError` is
    raised only once for the task.
    Docs: https://docs.python.org/3/library/asyncio-task.html#task-cancellation
     
    Currently is supported in Python 3.11+ due to using :ref:`asyncio.TaskGroup`.
    """

    class ListeningEvent(StartedListeningEvent):
        def __init__(self) -> None:
            self.event = asyncio.Event()

        async def set(self):
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self.event.set)

        async def wait(self):
            await self.event.wait()

    def __init__(
        self,
        backend: "CancellationBackend",
        task: Callable[Params, Coroutine[Any, Any, Result]],
        task_id: str,
    ):
        self.backend = backend
        self.task = task
        self.task_id = task_id

    async def __call__(self, *args: Params.args, **kwargs: Params.kwargs) -> Result:
        result: Result = None # type: ignore

        listener_exception: Exception | None = None
        task_exception: Exception | None = None
        cancelled_by_request: bool = False

        async def listen_for_cancellation(event: StartedListeningEvent):
            nonlocal listener_exception, cancelled_by_request

            try:
                await self.backend.listen_for_cancellation(self.task_id, event)
            except TaskCancellationException:
                cancelled_by_request = True
                raise
            except asyncio.CancelledError:
                raise
            except Exception as e:
                listener_exception = e
                raise

        async def call_task():
            nonlocal result, task_exception

            try:
                result = await self.task(*args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                task_exception = e
                raise

        try:
            async with asyncio.TaskGroup() as tg:
                # Listen before checking for cancellation in state holder
                # so the message won't get lost in non-persistent queues
                event = self.ListeningEvent()
                tg.create_task(listen_for_cancellation(event))
                await event.wait()

                if await self.backend.is_cancelled(self.task_id):
                    cancelled_by_request = True
                    raise StopTaskGroupException()

                task_task = asyncio.create_task(call_task())
                await task_task
                if not task_task.cancelled():
                    raise StopTaskGroupException()
        except* StopTaskGroupException:
            pass
        except* Exception as exc_group:
            uncaught_exceptions = list(
                filter(
                    lambda e: e == task_exception or e == listener_exception,
                    exc_group.exceptions,
                )
            )

            if uncaught_exceptions:
                logging.log(logging.ERROR, "Uncaught exceptions in TaskGroup")
                for e in uncaught_exceptions:
                    logging.exception(e)

        if task_exception is not None:
            raise task_exception
        elif cancelled_by_request:
            raise TaskCancellationException()
        elif listener_exception is not None:
            raise listener_exception
        else:
            return result
