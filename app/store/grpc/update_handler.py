from asyncio import Task
from datetime import datetime
from os.path import join, dirname
from typing import Optional

import typing
import asyncio

import aiofiles
import grpc
import ws_backend_pb2
import ws_backend_pb2_grpc


if typing.TYPE_CHECKING:
    from app.web.app import Application

class Handler:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.handle_task: Task |None

    async def start(self):
        print("manager init")
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle_update())


    async def stop(self):
        self.is_running = False
        self.handle_task.cancel()

    async def handle_update(self):
        while self.is_running:
            await asyncio.sleep(20)
            async with grpc.aio.insecure_channel('localhost:50051') as channel:
                stub = ws_backend_pb2_grpc.WS_Backend_ServiceStub(channel=channel)
                changes : ws_backend_pb2.GetUpdatesResponse = await stub.GetUpdates(ws_backend_pb2.GetUpdatesRequest())
                for doc in changes.res:
                    try:
                        current_doc = await self.app.store.docs.get_doc(int(doc.document_id))
                        async with aiofiles.open(
                                join(
                                    dirname(__file__),
                                    "..",
                                    "storage",
                                    f"{current_doc.owner.id}",
                                    f"""{current_doc.name}.txt""",
                                ),
                                mode="r+",
                        ) as editing:
                            lines =  await editing.readlines()
                            
                    except:
                        pass
                pass
            await asyncio.sleep(600)
