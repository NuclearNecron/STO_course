from aiohttp.web_app import Application


__all__ = ("register_urls",)


def register_urls(application: Application):
    from app.user.urls import register_urls as user_urls

    user_urls(application)
