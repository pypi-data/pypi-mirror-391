import time
import asyncio

import aio_pika
from taskiq.compat import model_dump, model_validate

from taskiq_cancellation.message import CancellationMessage

from .queue import QueueCancellationNotifier


class AioPikaNotifier(QueueCancellationNotifier):
    """Notifier for RabbitMQ using aio-pika"""

    EXCHANGE_NAME = "__taskiq_cancellation"

    def __init__(self, url: str, **connection_kwargs):
        """
        Creates AioPika notifier

        :param url: url to rabbitmq
        :type url: str
        :param connection_kwargs: arguments for :ref:`aio_pika.connect_robust`
        """
        super().__init__()

        self.url: str = url
        self.connection_kwargs = connection_kwargs

    async def cancel(self, task_id: str) -> None:
        timestamp = time.time()
        
        connection = await aio_pika.connect_robust(self.url, **self.connection_kwargs)

        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                self.EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT, durable=True
            )

            await exchange.publish(
                aio_pika.Message(
                    body=self.serializer.dumpb(
                        model_dump(
                            CancellationMessage(task_id=task_id, timestamp=timestamp)
                        )
                    )
                ),
                routing_key="",
            )

    async def _listen(self, started_listening: asyncio.Event):
        connection = await aio_pika.connect_robust(self.url, **self.connection_kwargs)

        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                self.EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT, durable=True
            )
            queue = await channel.declare_queue(exclusive=True, auto_delete=True)
            await queue.bind(exchange)

            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(started_listening.set)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    cancellation_message = model_validate(
                        CancellationMessage, self.serializer.loadb(message.body)
                    )

                    for subscriber_queue in self.queues:
                        await subscriber_queue.put(cancellation_message)
                    await message.ack()
