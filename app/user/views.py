from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import (
    request_schema,
    response_schema,
    docs,
)
from aiohttp_session import new_session

from app.web.app import View
from app.web.mixin import AuthRequiredMixin
from app.web.utils import json_response

from app.user.schemas import UserSchema, NewUserSchema


class UserLoginView(View):
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


class UserCurrentView(AuthRequiredMixin, View):
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


class UserCreate(View):
    @request_schema(NewUserSchema)
    async def post(self):
        admin = await self.store.user.create_user(
            login=self.data["login"],
            password=self.data["password"],
            nickname=self.data["nickname"],
        )
        return json_response(
            data={
                "id": admin.id,
                "login": admin.login,
                "nickname": admin.nickname,
            }
        )
