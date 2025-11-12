from taskiq_cancellation.abc import CancellationStateHolder


class InMemoryCancellationStateHolder(CancellationStateHolder):
    """In memory cancellation state holder used for testing"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.state_holder: dict[str, bool] = {}

    async def cancel(self, task_id: str) -> None:
        self.state_holder[task_id] = True

    async def is_cancelled(self, task_id: str) -> bool:
        return self.state_holder.get(task_id, False)
