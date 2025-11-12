import abc
import weakref
import asyncio
from typing import Union

from taskiq_cancellation.abc import CancellationNotifier, StartedListeningEvent
from taskiq_cancellation.exceptions import TaskCancellationException
from taskiq_cancellation.message import CancellationMessage


class QueueCancellationNotifier(CancellationNotifier):
    """
    A helper cancellation notifier that uses one listener to receive cancellation messages and
    notifies listeners from `listen_for_cancellation` via `asyncio.Queue`

    Requires :func:`_listen` to be implemeted
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.listener_task: Union[asyncio.Task, None] = None
        self.queues: weakref.WeakSet[asyncio.Queue[CancellationMessage]] = (
            weakref.WeakSet()
        )
        """Set of subscribers' `asyncio.Queue`s to populate when message's received"""

    async def shutdown(self) -> None:
        if self.listener_task is not None:
            self.listener_task.cancel()
            await asyncio.wait([self.listener_task])

    async def listen_for_cancellation(
        self, task_id: str, started_listening_event: StartedListeningEvent
    ) -> None:
        cancellations: asyncio.Queue[CancellationMessage] = asyncio.Queue()

        if self.listener_task is None:
            await self._create_listener_task()

        await self._subscribe(cancellations)
        await started_listening_event.set()

        while True:
            cancellation_message = await cancellations.get()

            if cancellation_message.task_id == task_id:
                raise TaskCancellationException()

    @abc.abstractmethod
    async def _listen(self, started_listening: asyncio.Event) -> None:
        """
        Listens for cancellation messages and put them into subscribers' `asyncio.Queue`s

        :param started_listening: event to be set when listener is ready to receive messages
        :type started_listening: asyncio.Event
        """
        pass

    async def _create_listener_task(self):
        if self.listener_task is not None:
            self.listener_task.cancel()

        started_listening = asyncio.Event()
        self.listener_task = asyncio.create_task(self._listen(started_listening))
        await started_listening.wait()

    async def _subscribe(self, queue: asyncio.Queue[CancellationMessage]):
        self.queues.add(queue)

    async def _unsubsribe(self, queue: asyncio.Queue[CancellationMessage]):
        self.queues.remove(queue)
