import sys
from typing import Callable, TYPE_CHECKING, Coroutine, Generic, Any

if sys.version_info >= (3, 11):
    from typing import ParamSpec, TypeVar
else:
    from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from taskiq_cancellation.abc.backend import CancellationBackend


Params = ParamSpec("Params")
Result = TypeVar("Result")


class EdgeCancellationHandler(Generic[Params, Result]):
    """
    Wrapper around a task function that handles cancellation

    Uses edge cancellation provided by asyncio. Currently is supported in Python 3.11+ due
    to using :ref:`asyncio.TaskGroup`.
    """

    def __init__(
        self,
        backend: "CancellationBackend",
        task: Callable[Params, Coroutine[Any, Any, Result]],
        task_id: str,
    ) -> None:
        raise NotImplementedError("Edge cancellation is not supported for Python <3.11")

    async def __call__(self, *args: Params.args, **kwargs: Params.kwargs) -> Result:
        raise NotImplementedError("Edge cancellation is not supported for Python <3.11")
