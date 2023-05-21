from typing import Optional

import aiohttp_cors
from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.store import setup_store, Store
from app.store.database.database import Database
from app.user.dataclasses import UserDC
from app.web.config import setup_config, Config
from app.web.logger import setup_logging
from aiohttp_session import setup as session_setup
from swagger_ui import api_doc

from app.web.middlewares import setup_middlewares
from app.web.routes import register_urls


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None


class Request(AiohttpRequest):
    user: UserDC | None = None

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
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    setup_logging(app)
    setup_config(app, config_path)
    session_setup(
        app,
        EncryptedCookieStorage(
            app.config.session.key,
            samesite="None",
            secure = True,
            domain=".together",
        ),
    )
    setup_middlewares(app)
    api_doc(
        app, config_path="swagger.json", url_prefix="/api/doc", title="API docs"
    )
    setup_aiohttp_apispec(app)
    register_urls(app, cors)
    setup_store(app)
    return app
