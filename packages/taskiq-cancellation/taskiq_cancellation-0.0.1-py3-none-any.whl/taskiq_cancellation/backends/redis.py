from taskiq_cancellation.backends.modular import ModularCancellationBackend

from taskiq_cancellation.notifiers.redis import PubSubCancellationNotifier
from taskiq_cancellation.state_holders.redis import RedisCancellationStateHolder


class RedisCancellationBackend(ModularCancellationBackend):
    def __init__(self, url: str, **kwargs) -> None:
        super().__init__(
            RedisCancellationStateHolder(url, **kwargs),
            PubSubCancellationNotifier(url, **kwargs),
        )
