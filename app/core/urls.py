import typing

if typing.TYPE_CHECKING:
    from app.core.application import Application


def setup_routes(app: "Application"):
    from app.core.views import WSConnectView

    app.router.add_view("/connect", WSConnectView)
