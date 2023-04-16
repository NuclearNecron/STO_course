from typing import Any

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)

# from app.store.database.database import Database
# from app.core.config import Config, setup_config
from app.core.logger import setup_logging

# from app.core.mw import setup_middlewares
from app.core.urls import setup_routes

# from app.admin.models import AdminDC
from app.store import Store, setup_store


# from aiohttp_apispec import setup_aiohttp_apispec
# from aiohttp_session import setup as session_setup
# from aiohttp_session.cookie_storage import EncryptedCookieStorage


class Application(AiohttpApplication):
    # config: Optional[Config] = None
    store: Store | None = None
    # database: Optional[Database] = None


class Request(AiohttpRequest):
    # TODO: set to None by default, change it in middleware
    user_credentials: Any = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    # @property
    # def database(self):
    #     return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app() -> Application:
    # setup_config(app)
    setup_logging(app)
    setup_routes(app)
    # setup_middlewares(app)
    setup_store(app)
    return app
