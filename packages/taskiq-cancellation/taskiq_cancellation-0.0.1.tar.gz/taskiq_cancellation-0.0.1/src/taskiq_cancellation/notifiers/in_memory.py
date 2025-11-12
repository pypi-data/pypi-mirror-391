import time
import asyncio
from typing import Union

from taskiq_cancellation.message import CancellationMessage

from .queue import QueueCancellationNotifier


class InMemoryCancellationNotifier(QueueCancellationNotifier):
    """In memory cancellation notifier used for testing"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # In Python 3.9 queues must be created inside a running loop
        # Source: https://stackoverflow.com/questions/53724665
        self.messages: Union[asyncio.Queue[CancellationMessage], None] = None

    async def cancel(self, task_id: str) -> None:
        if self.messages is None:
            self.messages = asyncio.Queue()

        timestamp = time.time()

        await self.messages.put(
            CancellationMessage(task_id=task_id, timestamp=timestamp)
        )

    async def _listen(self, started_listening: asyncio.Event) -> None:
        if self.messages is None:
            self.messages = asyncio.Queue()

        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(started_listening.set)

        while True:
            message = await self.messages.get()

            for queue in self.queues:
                await queue.put(message)
