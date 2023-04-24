import typing
from hashlib import sha256

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.user.dataclasses import UserDC, UserforRequest
from app.user.models import UserModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class UserAccessor(BaseAccessor):
    async def get_by_login(self, login: str) -> UserDC | None:
        async with self.app.database.session() as session:
            query = select(UserModel).where(UserModel.login == login)
            res = await session.scalars(query)
            user = res.one_or_none()
            if user:
                return UserDC(
                    id=user.id,
                    login=user.login,
                    password=user.password,
                    nickname=user.nickname,
                )
            return None

    async def create_user(
        self, login: str, password: str, nickname: str
    ) -> UserforRequest:
        async with self.app.database.session() as session:
            user = UserModel(
                login=login,
                password=sha256(password.encode()).hexdigest(),
                nickname=nickname,
            )
            session.add(user)
            await session.commit()
            return UserforRequest(
                id=user.id, login=user.login, nickname=nickname
            )
