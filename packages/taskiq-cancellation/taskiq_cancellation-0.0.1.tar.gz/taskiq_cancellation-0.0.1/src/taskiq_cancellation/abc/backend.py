import abc
import sys
import inspect
from typing import Callable, Annotated, overload, Optional, cast, Union

if sys.version_info >= (3, 11):
    from typing import Self, ParamSpec, TypeVar
else:
    from typing_extensions import Self, ParamSpec, TypeVar

from taskiq import Context, TaskiqDepends, AsyncBroker, TaskiqEvents, TaskiqState

from taskiq_cancellation.utils import combines
from taskiq_cancellation.cancellation_handlers import (
    CancellationType,
    LevelCancellationHandler,
    EdgeCancellationHandler,
)

from .started_listening_event import StartedListeningEvent


Params = ParamSpec("Params")
Result = TypeVar("Result")


class CancellationBackend(abc.ABC):
    """
    Base class for cancellation backend
    """

    def __init__(self) -> None:
        super().__init__()

        self.broker: Union[AsyncBroker, None] = None

    @abc.abstractmethod
    async def is_cancelled(self, task_id: str) -> bool:
        """
        Checks if a task with task id of *task_id* is set to be cancelled

        :param task_id: task id to check
        :type task_id: str
        :returns: task cancellation state
        :rtype: bool
        """
        pass

    @abc.abstractmethod
    async def cancel(self, task_id: str) -> None:
        """
        Cancels a task with task id of *task_id*

        :param task_id: id of the task to cancel
        :type task_id: str
        """
        pass

    @abc.abstractmethod
    async def listen_for_cancellation(
        self, task_id: str, started_listening_event: StartedListeningEvent
    ) -> None:
        """
        Listens for cancellation messages and raises :ref:`TaskCancellationException` when
        receives :ref:`CancellationMessage` with same id as *task_id*.

        This function is used in :func:`cancellable` decorator.
        Call `started_listening_task_status.started()` when the listener is ready
        to receive messages.

        :param task_id: id of task that will be listened for
        :type task_id: str
        :param started_listening_task_status:
        :type started_listening_task_status: anyio.abc.TaskStatus
        """
        pass

    async def startup(self) -> None:
        """
        Starts up cancellation backend

        Triggered only if backend has a broker set. To set a broker use :func:`with_broker`.
        """
        pass

    async def shutdown(self) -> None:
        """Shuts down cancellation backend

        Triggered only if backend has a broker set. To set a broker use :ref:`with_broker`.
        """
        pass

    def with_broker(self, broker: AsyncBroker) -> Self:
        """
        Set a broker and return updated cancellation backend

        Sets up startup and shutdown event handlers for backend's startup
        and shutdown methods respectfully

        :param broker: new broker
        :type broker: AsyncBroker
        :returns: self
        """
        if self.broker is not None:
            self.broker.event_handlers[TaskiqEvents.CLIENT_STARTUP].remove(
                self._broker_startup_handler
            )
            self.broker.event_handlers[TaskiqEvents.WORKER_STARTUP].remove(
                self._broker_startup_handler
            )
            self.broker.event_handlers[TaskiqEvents.CLIENT_SHUTDOWN].remove(
                self._broker_shutdown_handler
            )
            self.broker.event_handlers[TaskiqEvents.WORKER_SHUTDOWN].remove(
                self._broker_shutdown_handler
            )

        self.broker = broker
        self.broker.add_event_handler(
            TaskiqEvents.CLIENT_STARTUP, self._broker_startup_handler
        )
        self.broker.add_event_handler(
            TaskiqEvents.WORKER_STARTUP, self._broker_startup_handler
        )
        self.broker.add_event_handler(
            TaskiqEvents.CLIENT_SHUTDOWN, self._broker_shutdown_handler
        )
        self.broker.add_event_handler(
            TaskiqEvents.WORKER_SHUTDOWN, self._broker_shutdown_handler
        )

        return self

    @overload
    def cancellable(
        self, cancellation_type: Callable[Params, Result]
    ) -> Callable[Params, Result]:
        pass

    @overload
    def cancellable(
        self, cancellation_type: Optional[CancellationType] = None
    ) -> Callable[[Callable[Params, Result]], Callable[Params, Result]]:
        pass

    def cancellable(self, cancellation_type=None):
        """
        Decorator that makes funcion cancellable

        This decorator makes a new function that creates two tasks in :ref:`anyio.TaskGroup`:
        1. Cancellation message listener (uses :ref:`listen_for_cancellation`)
        2. Wrapped function

        - Returns function's result/exception if it finishes successfully/unsuccessfully
        - Raises :ref:`TaskCancellationException` if listener task receives cancellation message
        - If listener task raises an exception, task is cancelled and exception is propogated upwards

        :param cancellation_type: type of cancellation used 
        :type cancellation_type: CancellationType
        :returns: Cancellable task function
        """

        defaults = {"cancellation_type": CancellationType.LEVEL}

        def make_decorator(cancellation_type: CancellationType):
            def decorator(
                task: Callable[Params, Result], /
            ) -> Callable[Params, Result]:
                # Executor type depends on receiver configuration which we can't accessed in any way
                if not inspect.iscoroutinefunction(task):
                    raise ValueError("Can't cancel synchronous function")

                @combines(task)
                async def wrapper(
                    *args,
                    __taskiq_context: Annotated[Context, TaskiqDepends(Context)] = None,  # type: ignore
                    **kwargs,
                ) -> Result:
                    if __taskiq_context is None:
                        # Ran the function directly, without kiq
                        return await task(*args, **kwargs)

                    task_id = __taskiq_context.message.task_id

                    if cancellation_type is CancellationType.EDGE:
                        edge_handler = EdgeCancellationHandler(self, task, task_id)
                        return await edge_handler(*args, **kwargs)
                    elif cancellation_type is CancellationType.LEVEL:
                        level_handler = LevelCancellationHandler(self, task, task_id)
                        return await level_handler(*args, **kwargs)
                    else:
                        raise ValueError(
                            f"Unknown cancellation type: {cancellation_type!r}"
                        )

                # Wrapper adds a key-word only param with default value
                casted_wrapper = cast(Callable[Params, Result], wrapper)
                return casted_wrapper

            return decorator

        if callable(cancellation_type):
            return make_decorator(**defaults)(cancellation_type)
        else:
            return make_decorator(
                cancellation_type=cancellation_type or defaults["cancellation_type"]
            )

    async def _broker_startup_handler(self, _: TaskiqState) -> None:
        await self.startup()

    async def _broker_shutdown_handler(self, _: TaskiqState) -> None:
        await self.shutdown()
