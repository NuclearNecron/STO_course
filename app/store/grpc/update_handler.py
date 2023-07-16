import json
import os
from asyncio import Task
from datetime import datetime
from os.path import join, dirname
from typing import Optional

import typing
import asyncio

import aiofiles
import grpc
import app.store.grpc.ws_backend_pb2 as ws_backend_pb2
import app.store.grpc.ws_backend_pb2_grpc as ws_backend_pb2_grpc


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Handler:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.handle_task: Task | None

    async def start(self):
        print("manager init")
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle_update())

    async def stop(self):
        self.is_running = False
        self.handle_task.cancel()

    async def handle_update(self):
        await asyncio.sleep(10)
        while self.is_running:
            async with grpc.aio.insecure_channel(
                f"{self.app.config.grpc.host}:{self.app.config.grpc.port}",
            ) as channel:
                stub = ws_backend_pb2_grpc.WS_Backend_ServiceStub(
                    channel=channel
                )
                try:
                    changes: ws_backend_pb2.GetUpdatesResponse = (
                        await stub.GetUpdates(
                            ws_backend_pb2.GetUpdatesRequest()
                        )
                    )
                    self.app.logger.info(changes)
                    for doc in changes.res:
                        print(changes.res)
                        self.app.logger.info(doc)
                        try:
                            current_doc = await self.app.store.docs.get_doc(
                                int(doc.document_id)
                            )
                            async with aiofiles.open(
                                    join(
                                        dirname(dirname(dirname(__file__))),
                                        "storage",
                                        f"{current_doc.owner.id}",
                                        f"""{current_doc.name}.txt""",
                                    ),
                                    mode="r+",
                            ) as editing:
                                line = await editing.read()
                            async with aiofiles.open(
                                join(
                                    dirname(dirname(dirname(__file__))),
                                    "storage",
                                    f"{current_doc.owner.id}",
                                    f"""{current_doc.name}.txt""",
                                ),
                                mode="w+",
                            ) as editing:
                                for change in doc.update:
                                    dict_1 = json.loads(change)
                                    dict_change = dict_1["payload"]["update"]
                                    if dict_change["add"]==True:
                                        line = line[:dict_change["position"]]+dict_change["symbol"]+line[dict_change["position"]:]
                                    else:
                                        line = line[:dict_change["position"]]+line[dict_change["position"]+len(dict_change["symbol"]):]
                                await editing.write(line)
                            await self.app.store.docs.update_doc(
                                current_doc.name, datetime.now(), current_doc.id
                            )
                        except Exception as err:
                            self.app.logger.error("GRPC update error")
                            self.app.logger.error(err)
                            self.app.logger.error("No such file")
                except Exception as err:
                    print(err)
                    print(err.args)
            print("new cycle")
            await asyncio.sleep(600)
