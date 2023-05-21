from aiohttp.web_exceptions import (
    HTTPForbidden,
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPConflict,
)
from aiohttp_apispec import (
    request_schema,
)
import aiofiles.os as aios
from os.path import join, dirname

from aiohttp_cors import CorsViewMixin
from aiohttp_session import new_session

from app.web.app import View
from app.web.mixin import AuthRequiredMixin
from app.web.utils import json_response

from app.user.schemas import UserSchema, NewUserSchema


class UserLoginView(CorsViewMixin, View):
    @request_schema(UserSchema)
    async def post(self):
        logindata = await self.store.user.get_by_login(self.data["login"])
        if logindata is None:
            raise HTTPForbidden
        user_data = {
            "id": logindata.id,
            "login": logindata.login,
            "nickname": logindata.nickname,
        }
        if "password" in self.data and logindata.is_password_valid(
            self.data["password"]
        ):
            session = await new_session(request=self.request)
            session["user"] = user_data
            return json_response(data=user_data)
        raise HTTPForbidden


class UserCurrentView(AuthRequiredMixin, CorsViewMixin, View):
    async def get(self):
        if self.request.user is not None:
            return json_response(
                data={
                    "id": self.request.user.id,
                    "login": self.request.user.login,
                    "nickname": self.request.user.nickname,
                }
            )
        raise HTTPUnauthorized


class UserCreate(CorsViewMixin, View):
    @request_schema(NewUserSchema)
    async def post(self):
        user = await self.store.user.create_user(
            login=self.data["login"],
            password=self.data["password"],
            nickname=self.data["nickname"],
        )
        if user is None:
            raise HTTPConflict
        await aios.mkdir(join(dirname(__file__), "..", "storage", f"{user.id}"))
        return json_response(
            data={
                "id": user.id,
                "login": user.login,
                "nickname": user.nickname,
            }
        )
