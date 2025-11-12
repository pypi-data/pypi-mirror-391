import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from taskiq.abc.serializer import TaskiqSerializer 

from taskiq_cancellation.abc import (
    CancellationBackend,
    CancellationNotifier,
    CancellationStateHolder,
    StartedListeningEvent,
)

import anyio


class ModularCancellationBackend(CancellationBackend):
    """
    Modular cancellation backend made up of :class:`CancellationStateHolder`
    and :class:`CancellationNotifier`

    - `CancellationStateHolder` stores cancellation state and blocks the task from being run.
    - `CancellationNotifier` receives cancellation messages and cancels already running tasks.
    """

    def __init__(
        self, state_holder: CancellationStateHolder, notifier: CancellationNotifier
    ):
        super().__init__()

        self.notifier: CancellationNotifier = notifier
        self.state_holder: CancellationStateHolder = state_holder

    async def is_cancelled(self, task_id: str) -> bool:
        return await self.state_holder.is_cancelled(task_id)

    async def cancel(self, task_id: str):
        async with anyio.create_task_group() as group:
            group.start_soon(self.state_holder.cancel, task_id)
            group.start_soon(self.notifier.cancel, task_id)

    async def listen_for_cancellation(
        self, task_id: str, started_listening_event: StartedListeningEvent
    ):
        await self.notifier.listen_for_cancellation(task_id, started_listening_event)

    async def startup(self) -> None:
        await super().startup()
        await self.state_holder.startup()
        await self.notifier.startup()

    async def shutdown(self) -> None:
        await super().shutdown()
        await self.state_holder.shutdown()
        await self.notifier.shutdown()

    def with_serializer(self, serializer: TaskiqSerializer) -> Self:
        """
        Sets a serializer to be used by the notifier
        
        :param serializer: serializer for cancellation messages
        :type serializer: TaskiqSerializer
        :return: self
        """
        self.notifier = self.notifier.with_serializer(serializer)
        
        return self
