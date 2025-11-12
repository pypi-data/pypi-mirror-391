import asyncio

from taskiq_cancellation.abc import CancellationNotifier, StartedListeningEvent


class NullCancellationNotifier(CancellationNotifier):
    """
    \"Do nothing\" cancellation notifier

    May be useful if there's no need or ability to use an actual notifier
    """

    async def cancel(self, task_id: str) -> None:
        pass

    async def listen_for_cancellation(
        self, task_id: str, started_listening_event: StartedListeningEvent
    ) -> None:
        await started_listening_event.set()
        await asyncio.sleep(float("+inf"))
