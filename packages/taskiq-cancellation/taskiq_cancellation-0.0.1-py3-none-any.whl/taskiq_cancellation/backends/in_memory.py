from taskiq_cancellation.notifiers.in_memory import InMemoryCancellationNotifier
from taskiq_cancellation.state_holders.in_memory import InMemoryCancellationStateHolder

from .modular import ModularCancellationBackend


class InMemoryCancellationBackend(ModularCancellationBackend):
    """
    Cancellation backend that stores state and notifications in memory

    Useful for testing purposes
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            state_holder=InMemoryCancellationStateHolder(**kwargs),
            notifier=InMemoryCancellationNotifier(**kwargs),
        )
