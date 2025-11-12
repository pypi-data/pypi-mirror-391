import abc


class StartedListeningEvent(abc.ABC):
    """
    A confirmation event for listeners to mark that they started listening to messages. API is
    similar to :ref:`asyncio.Event`.

    This is needed for different cancellation types:
    - Level cancellation uses :ref:`anyio.abc.TaskStatus`
    - Edge cancellation uses :ref:`asyncio.Event`
    """

    @abc.abstractmethod
    async def set(self):
        """Sets the event"""
        pass

    @abc.abstractmethod
    async def wait(self):
        """Waits for the event to be set"""
        pass
