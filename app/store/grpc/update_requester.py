from typing import Optional, TYPE_CHECKING
from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.grpc.update_handler import Handler


if TYPE_CHECKING:
    from app.web.app import Application


class GRPCAPI(BaseAccessor):
    def __int__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.client: Optional[ClientSession] = None
        self.updater: Optional[Handler] = None

    async def connect(self, app: "Application"):
        self.client = ClientSession()
        self.updater = Handler(self.app)
        await self.updater.start()

    async def disconnect(self, app: "Application"):
        await self.client.close()
        await self.updater.stop()
        self.client = None
