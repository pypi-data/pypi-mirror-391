import sys
from collections.abc import Coroutine
from typing import Callable, TYPE_CHECKING, Generic, Union, cast, Any

if sys.version_info >= (3, 11):
    from typing import ParamSpec, TypeVar
else:
    from typing_extensions import ParamSpec, TypeVar

import anyio
from anyio.abc import TaskStatus

from taskiq_cancellation.abc.started_listening_event import StartedListeningEvent
from taskiq_cancellation.exceptions import TaskCancellationException

if TYPE_CHECKING:
    from taskiq_cancellation.abc.backend import CancellationBackend


Params = ParamSpec("Params")
Result = TypeVar("Result")


class LevelCancellationHandler(Generic[Params, Result]):
    """
    Wrapper around a task function that handles cancellation

    Uses level cancellation provided by anyio. That means cancellation exception is raised
    on every await in the coroutine.
    Docs: https://anyio.readthedocs.io/en/stable/cancellation.html#differences-between-asyncio-and-anyio-cancellation-semantics
    """

    class ListeningEvent(StartedListeningEvent):
        def __init__(self, task_status: TaskStatus) -> None:
            self.task_status = task_status

        async def set(self):
            self.task_status.started()

        async def wait(self):
            # Can ignore, won't execute further before task status is set
            pass

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
        result: Union[Result, None] = None

        listener_exception: Union[Exception, None] = None
        task_exception: Union[Exception, None] = None
        cancelled_by_request: bool = False

        async with anyio.create_task_group() as group:

            async def listen_for_cancellation(
                task_status: TaskStatus[None] = anyio.TASK_STATUS_IGNORED,
            ):
                nonlocal listener_exception, cancelled_by_request

                event = self.ListeningEvent(task_status)
                try:
                    await self.backend.listen_for_cancellation(self.task_id, event)
                except TaskCancellationException:
                    cancelled_by_request = True
                except anyio.get_cancelled_exc_class():
                    pass
                except Exception as e:
                    listener_exception = e
                finally:
                    group.cancel_scope.cancel()

            async def call_task():
                nonlocal result, task_exception

                try:
                    result = await self.task(*args, **kwargs)
                except anyio.get_cancelled_exc_class():
                    pass
                except Exception as e:
                    task_exception = e
                finally:
                    group.cancel_scope.cancel()

            # Listen before checking for cancellation in state holder
            # so the message won't get lost in non-persistent queues
            await group.start(listen_for_cancellation)
            if await self.backend.is_cancelled(self.task_id):
                cancelled_by_request = True
                group.cancel_scope.cancel()
            else:
                group.start_soon(call_task)

        if task_exception is not None:
            raise task_exception
        elif cancelled_by_request:
            raise TaskCancellationException()
        elif listener_exception is not None:
            raise listener_exception
        else:
            # If the task is finished, it is definitely not None
            result = cast(Result, result)
            return result
