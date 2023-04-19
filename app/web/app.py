from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.store import setup_store, Store
from app.store.database.database import Database
from app.web.config import setup_config, Config
from app.web.logger import setup_logging
from aiohttp_session import setup as session_setup
from swagger_ui import api_doc

from app.web.middlewares import setup_middlewares


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None


class Request(AiohttpRequest):
    user: User | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

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
    setup_middlewares(app)
    api_doc(
        app, config_path="swagger.json", url_prefix="/api/doc", title="API docs"
    )
    # register_urls(app)
    setup_store(app)

    return app
