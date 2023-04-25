from aiohttp.web_app import Application

__all__ = ("register_urls",)

from app.docs.views import (
    CreateDocView,
    ListDocsView,
    GetFileView,
    ManageDocView,
    ManageShareView,
)


def register_urls(application: Application):

    application.router.add_view("/doc/create", CreateDocView)
    application.router.add_view("/doc/list", ListDocsView)
    application.router.add_view("/doc/get/{doc_id}", GetFileView)
    application.router.add_view("/doc/{doc_id}", ManageDocView)
    application.router.add_view("/doc/share/{doc_id}", ManageShareView)
