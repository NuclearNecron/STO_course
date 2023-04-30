from redis.asyncio.client import Pipeline
from redis.exceptions import WatchError

from app.base.base_accessor import BaseAccessor


class RedisAccessor(BaseAccessor):
    async def append_update(self, document: str, change: str):
        await self.app.redis.connection.rpush(document, change)
        return

    async def get_all_updates(self, document: str) -> list[str]:
        return await self.app.redis.connection.lrange(document, 0, -1)

    async def delete_document(self, document: str):
        await self.app.redis.connection.delete(document)
        return

    async def filter_updates(
        self, document: str, timestamp: str | None = None
    ):
        """Атомарная фильтрация списка обновлений по ключу и временной метке"""
        if timestamp:
            async_pipe: Pipeline
            async with self.app.redis.connection.pipeline() as async_pipe:
                while True:
                    try:
                        await async_pipe.watch(document)
                        current_updates = async_pipe.get(document)
                        # TODO: отфильтровать изменения по временной метке
                        # filtered_updates = filter(lambda update: True, current_updates)
                        filtered_updates = (
                            current_updates  # убрать эту заглушку
                        )
                        async_pipe.multi()
                        async_pipe.set(document, filtered_updates)
                        await async_pipe.execute()
                        break
                    except WatchError:
                        continue
        return

    async def get_all_documents_updates(self) -> dict[str, list[str]] | None:
        res = {}
        async for doc_key in self.app.redis.connection.scan_iter():
            res[doc_key] = await self.get_all_updates(document=doc_key)
        return res if res else None
