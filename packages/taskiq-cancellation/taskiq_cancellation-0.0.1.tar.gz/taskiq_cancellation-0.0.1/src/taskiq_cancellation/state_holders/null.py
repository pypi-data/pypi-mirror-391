from taskiq_cancellation.abc import CancellationStateHolder


class NullCancellationStateHolder(CancellationStateHolder):
    """
    \"Do nothing\" cancellation state holder

    May be useful if there's no need or ability to use an actual state holder
    """

    async def cancel(self, task_id: str) -> None:
        pass

    async def is_cancelled(self, task_id: str) -> bool:
        return False
