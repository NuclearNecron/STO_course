import typing

from app.store.database.database import Database
from app.store.docs.accessor import DocsAccessor
from app.store.grpc.update_requester import GRPCAPI
from app.store.user.accessor import UserAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.user = UserAccessor(app)
        self.docs = DocsAccessor(app)
        self.grpc = GRPCAPI(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
