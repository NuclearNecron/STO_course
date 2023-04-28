import typing

from app.grpcio.server import gRPCServer
from app.store.redis.database import RedisDB

if typing.TYPE_CHECKING:
    from app.core.application import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.ws.accessor import WSAccessor
        from app.store.redis.accessor import RedisAccessor

        self.ws = WSAccessor(app)
        self.redis = RedisAccessor(app)


def setup_store(app: "Application"):
    app.redis = RedisDB(app)
    app.on_startup.append(app.redis.connect)
    app.on_cleanup.append(app.redis.disconnect)

    app.grpc_server = gRPCServer(app)
    app.on_startup.append(app.grpc_server.serve)
    app.on_cleanup.append(app.grpc_server.finish)

    app.store = Store(app)
