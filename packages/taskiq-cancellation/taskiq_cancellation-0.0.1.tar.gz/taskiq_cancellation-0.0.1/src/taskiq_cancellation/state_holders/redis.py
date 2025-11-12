from taskiq_cancellation.abc import CancellationStateHolder

import redis.asyncio as redis


class RedisCancellationStateHolder(CancellationStateHolder):
    def __init__(self, url: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection_pool = redis.BlockingConnectionPool.from_url(url, **kwargs)

    async def cancel(self, task_id: str) -> None:
        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            await conn.set(self._task_key(task_id), str(True))

    async def is_cancelled(self, task_id: str) -> bool:
        async with redis.Redis(connection_pool=self.connection_pool) as conn:
            response = await conn.get(self._task_key(task_id))
            return bool(response)

    async def shutdown(self) -> None:
        await super().shutdown()
        await self.connection_pool.aclose()

    def _task_key(self, task_id: str) -> str:
        return f"__cancellation_status_{task_id}"
    
