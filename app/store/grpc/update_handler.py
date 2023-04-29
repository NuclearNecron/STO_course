import json
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
                            for change in doc.update:
                                dict_change = json.loads(change)
                                if dict_change["letter"]=="/n" and dict_change["insert"] == True:
                                    temp = lines[dict_change["line"]][dict_change["symbol"]:]
                                    lines[dict_change["line"]]=lines[dict_change["line"]][:dict_change["symbol"]]+"/n"
                                    lines.insert(dict_change["line"]+1,temp)
                                elif dict_change["symbol"]=="/n" and dict_change["insert"] == False:
                                    lines[dict_change["line"]] = lines[dict_change["line"]][
                                                                 :-2] + lines[dict_change["line"]+1]
                                    lines.pop(dict_change["line"]+1)
                                elif len(dict_change["letter"])>1 and dict_change["insert"] == True:
                                    lines[dict_change["line"]] = lines[dict_change["line"]][:dict_change["symbol"]]+dict_change["letter"]+lines[dict_change["line"]][dict_change["symbol"]:]
                                    await editing.truncate(0)
                                    await editing.writelines(lines)
                                    lines = await editing.readlines()
                                elif len(dict_change["letter"])>1 and dict_change["insert"] == False:
                                    removed_lines= dict_change["letter"].count("/n")
                                    new_line = ""
                                    for i in range(removed_lines):
                                        new_line+= lines[dict_change["line"]+i]
                                        lines.pop(dict_change["line"]+i)
                                    new_line.replace(dict_change["letter"],"",1)
                                    lines.insert(dict_change["line"])
                                    await editing.truncate(0)
                                    await editing.writelines(lines)
                                    lines = await editing.readlines()
                                elif dict_change["insert"]:
                                    lines[dict_change["line"]] = lines[dict_change["line"]][
                                                                 :dict_change["symbol"]] + dict_change["letter"]+lines[dict_change["line"]][
                                                                 dict_change["symbol"]:]
                                else:
                                    lines[dict_change["line"]] = lines[dict_change["line"]][
                                                                 :dict_change["symbol"]] + \
                                                                 lines[dict_change["line"]][
                                                                 dict_change["symbol"]+1:]
                            await editing.truncate(0)
                            await editing.writelines(lines)
                        await self.app.store.docs.update_doc(current_doc.name,datetime.now(),current_doc.id)
                    except:
                        pass
            await asyncio.sleep(600)
