from typing import Any

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.core.config import setup_config, Config
from app.core.logger import setup_logging
from app.core.middlewares import setup_middlewares
from app.core.urls import setup_routes
from app.grpcio.server import gRPCServer
from app.store import Store, setup_store, RedisDB


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    redis: RedisDB | None = None
    grpc_server: gRPCServer | None = None


class Request(AiohttpRequest):
    user_credentials: Any = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def redis(self):
        return self.request.app.redis

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    return app
