import typing

from app.store.redis.database import RedisDB

if typing.TYPE_CHECKING:
    from app.core.application import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.ws.accessor import WSAccessor

        self.ws = WSAccessor(app)


def setup_store(app: "Application"):
    app.redis = RedisDB(app)
    app.on_startup.append(app.redis.connect)
    app.on_cleanup.append(app.redis.disconnect)
    app.store = Store(app)
