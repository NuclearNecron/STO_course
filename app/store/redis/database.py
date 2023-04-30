import typing

from redis.asyncio import Redis

if typing.TYPE_CHECKING:
    from app.core.application import Application


class RedisDB:
    def __init__(self, app: "Application"):
        self.app = app
        self.connection: Redis | None = None

    async def connect(self, *_: list, **__: dict):
        self.connection = Redis(
            host=self.app.config.redis.host,
            port=self.app.config.redis.port,
            db=self.app.config.redis.db,
            decode_responses=True,
        )
        self.app.logger.info(
            f"Ping Redis-server successfully: {await self.connection.ping()}"
        )

    async def disconnect(self, *_: list, **__: dict):
        if self.connection:
            await self.connection.close()
            self.connection = None
