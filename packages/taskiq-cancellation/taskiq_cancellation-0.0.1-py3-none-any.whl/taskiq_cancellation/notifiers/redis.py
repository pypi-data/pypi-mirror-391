import time
import asyncio

import redis.asyncio as redis
from taskiq.compat import model_dump, model_validate

from taskiq_cancellation.message import CancellationMessage

from .queue import QueueCancellationNotifier


class PubSubCancellationNotifier(QueueCancellationNotifier):
    """Cancellation notifier using Redis pub/sub"""
    
    CHANNEL_NAME = "__taskiq_cancellation_notifications"

    def __init__(self, url: str, **connection_kwargs) -> None:
        """
        Creates AioPika notifier

        :param url: url to redis
        :type url: str
        :param connection_kwargs: arguments for :ref:`redis.BlockingConnectionPool.from_url`
        """
        super().__init__()

        self.connection_pool = redis.BlockingConnectionPool.from_url(url, **connection_kwargs)

    async def cancel(self, task_id: str) -> None:
        timestamp = time.time()

        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            await conn.publish(
                self.CHANNEL_NAME,
                self.serializer.dumpb(
                    model_dump(
                        CancellationMessage(task_id=task_id, timestamp=timestamp)
                    )
                ),
            )

    async def _listen(self, started_listening: asyncio.Event):
        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            pubsub = conn.pubsub()
            await pubsub.subscribe(self.CHANNEL_NAME)

            # started_listening.set()
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(started_listening.set)

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=None
                )

                if message is None:
                    continue
                if message["type"] != "message":
                    continue

                cancellation_message = model_validate(
                    CancellationMessage, self.serializer.loadb(message["data"])
                )
                for queue in self.queues:
                    await queue.put(cancellation_message)

    async def shutdown(self) -> None:
        await super().shutdown()
        await self.connection_pool.aclose()
    