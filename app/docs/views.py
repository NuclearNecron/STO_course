from app.web.app import View
from app.web.mixin import AuthRequiredMixin


class CreateDocView(AuthRequiredMixin, View):
    async def post(self):
        pass


class ListDocsView(AuthRequiredMixin, View):
    async def get(self):
        pass


class ManageDocView(AuthRequiredMixin, View):
    async def get(self):
        pass

    async def put(self):
        pass

    async def delete(self):
        pass


class ManageShareView(AuthRequiredMixin, View):
    async def post(self):
        pass

    async def put(self):
        pass

    async def get(self):
        pass

    async def delete(self):
        pass
