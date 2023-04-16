import typing

if typing.TYPE_CHECKING:
    from app.core.application import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.ws.accessor import WSAccessor

        self.ws = WSAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
