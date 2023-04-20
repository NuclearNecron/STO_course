from app.base.base_accessor import BaseAccessor
from app.store.ws.schemes import EventSchema


class RedisAccessor(BaseAccessor):

    async def append_update(self, document: str, change: str):
        await self.app.redis.connection.rpush(document, change)
        return

    async def get_all_updates(self, document: str):
        raw_res = await self.app.redis.connection.lrange(document, 0, -1)
        return raw_res
