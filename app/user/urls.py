from aiohttp.web_app import Application

__all__ = ("register_urls",)


def register_urls(application: Application):

    from app.user.views import UserLoginView

    application.router.add_view("/user.login", UserLoginView)
    from app.user.views import UserCurrentView

    application.router.add_view("/user.current", UserCurrentView)

    from app.user.views import UserCreate

    application.router.add_view("/user.create", UserCreate)
