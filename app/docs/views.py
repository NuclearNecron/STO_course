import json
from datetime import datetime
from os.path import join, dirname
from ast import literal_eval

from aiohttp.web_exceptions import (
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPConflict,
    HTTPForbidden,
    HTTPNotFound,
)
from aiohttp.web_fileresponse import FileResponse
from aiohttp_apispec import request_schema
import aiofiles
import aiofiles.os as aios
from aiohttp_cors import CorsViewMixin

from app.docs.schemas import NewDocSchema, ConnectionSchema, UpdDocSchema
from app.web.app import View
from app.web.mixin import AuthRequiredMixin
from app.web.utils import json_response, AccessState
import grpc
import app.store.grpc.ws_backend_pb2 as backend_pb2
import app.store.grpc.ws_backend_pb2_grpc as backend_pb2_grpc


class CreateDocView(CorsViewMixin, View):
    @request_schema(NewDocSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        newfiledata = self.data
        new_file = await self.store.docs.create_doc(
            name=newfiledata["name"],
            owner_id=self.request.user.id,
            timestamp=newfiledata["timestamp"].replace(tzinfo=None),
        )
        if new_file is None:
            raise HTTPConflict
        handlefile = await aiofiles.open(
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{self.request.user.id}",
                f"{new_file.name}.txt",
            ),
            mode="x",
        )
        await handlefile.close()
        return json_response(
            data={
                "id": new_file.id,
                "name": new_file.name,
                "last_edited": str(new_file.last_edited),
                "owner_id": new_file.owner_id,
            }
        )


class ListDocsView( CorsViewMixin, View):
    async def get(self):
        if not getattr(self.request, "user", None):
            raise HTTPUnauthorized
        if self.request.user is None:
            raise HTTPUnauthorized
        fileslist = await self.store.docs.get_list_docs(self.request.user.id)
        return json_response(
            data={
                "docs": [
                    {
                        "id": file.id,
                        "name": file.name,
                        "last_edited": str(file.last_edited),
                        "owner": {
                            "id": file.owner.id,
                            "nickname": file.owner.nickname,
                        },
                    }
                    for file in fileslist
                ]
            }
        )


class GetFileView(CorsViewMixin, View):
    async def get(self):
        if not getattr(self.request, "user", None):
            raise HTTPUnauthorized
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc_db = await self.store.docs.get_doc(doc_id)
        if doc_db is None:
            raise HTTPNotFound
        ownership = await self.store.docs.get_user_access_to_doc(
            self.request.user.id, doc_id
        )
        if ownership is None:
            raise HTTPForbidden
        async with aiofiles.open(
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{doc_db.owner.id}",
                f"""{doc_db.name}.txt""",
            ),
            mode="r+",
        ) as editing:
            lines = await editing.read()
        # return FileResponse(
        #     path=join(
        #         dirname(__file__),
        #         "..",
        #         "storage",
        #         f"{self.request.user.id}",
        #         f"{doc_db.name}.txt",
        #     )
        # )
        return json_response(
            data={
                "res": lines,
            }
        )


class ManageDocView(CorsViewMixin, View):
    async def get(self):
        if not getattr(self.request, "user", None):
            raise HTTPUnauthorized
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc_db = await self.store.docs.get_doc(doc_id)
        if doc_db is None:
            raise HTTPNotFound
        ownership = await self.store.docs.get_user_access_to_doc(
            self.request.user.id, doc_id
        )
        if ownership is None:
            raise HTTPForbidden
        return json_response(
            data={
                "id": doc_db.id,
                "name": doc_db.name,
                "last_edited": str(doc_db.last_edited),
                "owner": {
                    "id": doc_db.owner.id,
                    "nickname": doc_db.owner.nickname,
                },
            }
        )

    @request_schema(UpdDocSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        # reqdata = await self.request.post()
        # bytearray = reqdata["data"]
        # new_data = literal_eval(bytearray.decode("utf-8"))
        # file = reqdata["text"]
        # # bytefile = file.file.read()
        # new_text = file.decode("utf-8")
        request_data = self.data
        new_data = request_data["data"]
        new_text = request_data["text"]
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        old_doc = await self.store.docs.get_doc(doc_id)
        if old_doc is None:
            raise HTTPNotFound
        ownership = await self.store.docs.get_user_access_to_doc(
            self.request.user.id, doc_id
        )
        if ownership is None or ownership.access != AccessState.WRITE.value:
            raise HTTPForbidden
        async with grpc.aio.insecure_channel(
            f"{self.request.app.config.grpc.host}:{self.request.app.config.grpc.port}"
        ) as channel:
            stub = backend_pb2_grpc.WS_Backend_ServiceStub(channel=channel)
            check = new_data["timestamp"]
            res = await stub.SendTimestamp(
                backend_pb2.SendTimestampRequest(
                    document_id=str(doc_id), timestamp=new_data["timestamp"]
                )
            )
            print(res)
        try:
            upd_doc = await self.store.docs.update_doc(
                name=new_data["name"],
                timestamp=datetime.strptime(
                    new_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                doc_id=int(doc_id),
            )
            if upd_doc is None:
                raise HTTPBadRequest
        except:
            raise HTTPBadRequest
        await aios.rename(
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{old_doc.owner.id}",
                f"{old_doc.name}.txt",
            ),
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{old_doc.owner.id}",
                f"""{new_data["name"]}.txt""",
            ),
        )

        async with aiofiles.open(
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{old_doc.owner.id }",
                f"""{new_data["name"]}.txt""",
            ),
            mode="w",
        ) as editing:
            await editing.truncate(0)
            await editing.write(new_text)

        return json_response(
            data={
                "id": doc_id,
                "name": new_data["name"],
                "last_edited": new_data["timestamp"],
                "owner": {
                    "id": old_doc.owner.id,
                    "nickname": old_doc.owner.nickname,
                },
            }
        )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc = await self.store.docs.get_doc(doc_id)
        if doc is None:
            raise HTTPNotFound
        ownership = await self.store.docs.check_ownership(
            doc_id, self.request.user.id
        )
        if ownership is None:
            raise HTTPForbidden
        await self.store.docs.delete_doc(doc_id)
        await aios.remove(
            join(
                dirname(__file__),
                "..",
                "storage",
                f"{doc.owner.id}",
                f"{doc.name}.txt",
            )
        )
        async with grpc.aio.insecure_channel(
            f"{self.request.app.config.grpc.host}:{self.request.app.config.grpc.port}"
        ) as channel:
            stub = backend_pb2_grpc.WS_Backend_ServiceStub(channel=channel)
            await stub.HandleDelete(
                backend_pb2.HandleDeleteRequest(document_id=str(doc_id))
            )
        return json_response(data={"result": "succesful"})


class ManageShareView(CorsViewMixin, View):
    @request_schema(ConnectionSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        newconnectiondata = self.data
        doc = await self.store.docs.get_doc(doc_id)
        if doc is None:
            raise HTTPNotFound
        ownership = await self.store.docs.check_ownership(
            doc_id, self.request.user.id
        )
        if ownership is None:
            raise HTTPForbidden
        user = await self.store.user.get_by_id(newconnectiondata["user"])
        if user is None:
            raise HTTPNotFound
        if AccessState.READ.value == newconnectiondata["rights"].upper():
            accesstype = AccessState.READ.value
        elif AccessState.WRITE.value == newconnectiondata["rights"].upper():
            accesstype = AccessState.WRITE.value
        else:
            raise HTTPBadRequest
        newconnection = await self.store.docs.add_user_to_doc(
            accesstype, user.id, doc_id
        )
        if newconnection is None:
            raise HTTPConflict
        return json_response(
            data={
                "user": {"id": user.id, "nickname": user.nickname},
                "doc_id": doc_id,
                "rights": accesstype,
            }
        )

    @request_schema(ConnectionSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        newconnectiondata = self.data
        doc = await self.store.docs.get_doc(doc_id)
        if doc is None:
            raise HTTPNotFound
        ownership = await self.store.docs.check_ownership(
            doc_id, self.request.user.id
        )
        if ownership is None:
            raise HTTPForbidden
        user = await self.store.user.get_by_id(newconnectiondata["user"])
        if user is None:
            raise HTTPNotFound
        if AccessState.READ.value == newconnectiondata["rights"].upper():
            accesstype = AccessState.READ.value
        elif AccessState.WRITE.value == newconnectiondata["rights"].upper():
            accesstype = AccessState.WRITE.value
        else:
            raise HTTPBadRequest
        newconnection = await self.store.docs.update_user_access_to_doc(
            accesstype, user.id, doc_id
        )
        return json_response(
            data={
                "user": {"id": user.id, "nickname": user.nickname},
                "doc_id": doc_id,
                "rights": accesstype,
            }
        )

    async def get(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc = await self.store.docs.get_doc(doc_id)
        if doc is None:
            raise HTTPNotFound
        ownership = await self.store.docs.get_user_access_to_doc(
            self.request.user.id, doc_id
        )
        if ownership is None:
            raise HTTPForbidden
        try:
            user_id = self.request.query["userId"]
            user = await self.store.user.get_by_id(int(user_id))
            if user is None:
                raise HTTPNotFound
            connections = await self.store.docs.get_user_access_to_doc(
                user.id, doc_id
            )
            if connections is None:
                raise HTTPNotFound
            return json_response(
                data={
                    "result": [
                        {
                            "user": {"id": user.id, "nickname": user.nickname},
                            "doc_id": doc_id,
                            "rights": connections.access,
                        }
                    ]
                }
            )
        except KeyError:
            connections = await self.store.docs.get_accesses_to_doc(
                doc_id=doc_id
            )
            return json_response(
                data={
                    "result": [
                        {
                            "user": {
                                "id": connection.user.id,
                                "nickname": connection.user.nickname,
                            },
                            "doc_id": doc_id,
                            "rights": connection.access,
                        }
                        for connection in connections
                    ]
                }
            )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            user_id = self.request.query["userId"]
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc = await self.store.docs.get_doc(doc_id)
        if doc is None:
            raise HTTPNotFound
        if int(user_id) == self.request.user.id:
            raise HTTPBadRequest
        ownership = await self.store.docs.check_ownership(
            doc_id, self.request.user.id
        )
        if ownership is None:
            raise HTTPForbidden
        user = await self.store.user.get_by_id(int(user_id))
        if user is None:
            raise HTTPNotFound
        connection = await self.store.docs.get_user_access_to_doc(
            user.id, doc_id
        )
        if connection is None:
            raise HTTPNotFound
        async with grpc.aio.insecure_channel(
            f"{self.request.app.config.grpc.host}:{self.request.app.config.grpc.port}"
        ) as channel:
            stub = backend_pb2_grpc.WS_Backend_ServiceStub(channel=channel)
            res = await stub.RemoveAccess(
                backend_pb2.RemoveAccessRequest(
                    document_id=str(doc_id), user_id=str(user.id)
                )
            )
            print (res)
        await self.store.docs.remove_user_access(user.id, doc_id)
        return json_response(data={"status": "success"})
