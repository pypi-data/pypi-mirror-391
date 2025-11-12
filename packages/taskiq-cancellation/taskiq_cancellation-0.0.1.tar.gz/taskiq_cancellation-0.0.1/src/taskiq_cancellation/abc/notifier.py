import sys
import abc

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from taskiq.abc.serializer import TaskiqSerializer
from taskiq.serializers import JSONSerializer

from .started_listening_event import StartedListeningEvent


class CancellationNotifier(abc.ABC):
    """Receives cancellation messages and notifies listeners of these messages"""

    def __init__(self):
        self.serializer = JSONSerializer()

    async def startup(self) -> None:
        """Starts up cancellation notifier"""
        pass

    async def shutdown(self) -> None:
        """Shuts down cancellation notifier"""
        pass

    @abc.abstractmethod
    async def cancel(self, task_id: str) -> None:
        """
        Sends a cancellation message of a task with task id of *task_id*

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

        This function is used in :func:`cancellable` decorator of :ref:`ModularCancellationBackend`.
        Call `started_listening_event.set()` when the listener is ready to receive messages.

        :param task_id: id of task that will be listened for
        :type task_id: str
        :param started_listening_event: "listener started listening" confirmation event
        :type started_listening_event: StartedListeningEvent
        """
        pass

    def with_serializer(self, serializer: TaskiqSerializer) -> Self:
        """
        Sets a serializer to be used by the notifier
        
        :param serializer: serializer for cancellation messages
        :type serializer: TaskiqSerializer
        :return: self
        """
        self.serializer = serializer

        return self
