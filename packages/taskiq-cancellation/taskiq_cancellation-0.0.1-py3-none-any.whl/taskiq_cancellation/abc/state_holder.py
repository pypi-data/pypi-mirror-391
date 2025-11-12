import abc


class CancellationStateHolder(abc.ABC):
    """Holds cancellation state of Taskiq tasks"""

    @abc.abstractmethod
    async def cancel(self, task_id: str) -> None:
        """
        Sets a state of task with task id of *task_id* to be cancelled

        :param task_id: id of the task to cancel
        :type task_id: str
        """
        pass

    @abc.abstractmethod
    async def is_cancelled(self, task_id: str) -> bool:
        """
        Checks if a task with task id of *task_id* is set to be cancelled

        :param task_id: task id to check
        :type task_id: str
        :returns: task cancellation state
        :rtype: bool
        """
        pass

    async def startup(self) -> None:
        """Starts up cancellation state holder"""
        pass

    async def shutdown(self) -> None:
        """Shuts down cancellation state holder"""
        pass
