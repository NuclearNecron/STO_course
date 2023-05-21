from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig, CorsViewMixin


__all__ = ("register_urls",)


def register_urls(application: Application, cors: CorsConfig):
    from app.user.urls import register_urls as user_urls
    from app.docs.urls import register_urls as docs_urls

    user_urls(application)
    docs_urls(application)
    for route in list(application.router.routes()):
        cors.add(route)
