import json
from datetime import datetime
from os.path import join, dirname
from ast import literal_eval

from aiohttp.web_exceptions import (
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPConflict, HTTPForbidden,
)
from aiohttp.web_fileresponse import FileResponse
from aiohttp_apispec import request_schema
import aiofiles
import aiofiles.os as aios

from app.docs.schemas import NewDocSchema
from app.web.app import View
from app.web.mixin import AuthRequiredMixin
from app.web.utils import json_response, AccessState


class CreateDocView(AuthRequiredMixin, View):
    @request_schema(NewDocSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        newfiledata = self.data
        new_file = await self.store.docs.create_doc(
            name=newfiledata["name"],
            owner_id=self.request.user.id,
            timestamp=newfiledata["timestamp"],
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


class ListDocsView(AuthRequiredMixin, View):
    async def get(self):
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


class GetFileView(AuthRequiredMixin, View):
    async def get(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc_db = await self.store.docs.get_doc(doc_id)
        if doc_db is None:
            raise HTTPBadRequest
        ownership = await self.store.docs.get_user_access_to_doc(self.request.user.id,doc_id)
        if ownership is None:
            raise HTTPForbidden
        return FileResponse(path=join(
                dirname(__file__),
                "..",
                "storage",
                f"{self.request.user.id}",
                f"{doc_db.name}.txt",
            ))


class ManageDocView(AuthRequiredMixin, View):
    async def get(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        doc_db = await self.store.docs.get_doc(doc_id)
        if doc_db is None:
            raise HTTPBadRequest
        ownership = await self.store.docs.get_user_access_to_doc(self.request.user.id,doc_id)
        if ownership is None:
            raise HTTPForbidden
        return json_response(data={
                "id": doc_db.id,
                "name": doc_db.name,
                "last_edited": str(doc_db.last_edited),
                "owner": {
                    "id": doc_db.owner.id,
                    "nickname": doc_db.owner.nickname,
                },

        })

    # @request_schema(NewDocSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        reqdata = await self.request.post()
        bytearray = reqdata['data']
        new_data = literal_eval(bytearray.decode('utf-8'))
        file = reqdata['text']
        bytefile = file.file.read()
        new_text = bytefile.decode("utf-8")
        try:
            doc_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest
        old_doc = await self.store.docs.get_doc(doc_id)
        if old_doc is None:
            raise HTTPBadRequest
        ownership = await self.store.docs.get_user_access_to_doc(self.request.user.id,doc_id)
        if ownership is None or ownership.access != AccessState.WRITE.value:
            raise HTTPForbidden
        upd_doc = await self.store.docs.update_doc(
            name=new_data["name"],
            timestamp=datetime.strptime(new_data["timestamp"],'%Y-%m-%d %H:%M:%S.%f'),
            doc_id=int(doc_id))
        if upd_doc is None:
            raise HTTPBadRequest
        await aios.rename(join(
                dirname(__file__),
                "..",
                "storage",
                f"{old_doc.owner.id}",
                f"{old_doc.name}.txt",
            ),join(
                dirname(__file__),
                "..",
                "storage",
                f"{old_doc.owner.id}",
                f"""{new_data["name"]}.txt""",
            ))

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
        return json_response(data={
            "id": doc_id,
            "name": new_data["name"],
            "last_edited": new_data["timestamp"],
            "owner": {
                "id": old_doc.owner.id,
                "nickname": old_doc.owner.nickname,
            },
        })

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
