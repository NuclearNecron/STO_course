from dataclasses import dataclass
from hashlib import sha256

from aiohttp_session import Session


@dataclass
class UserforRequest:
    id: int
    login: str
    nickname: str


@dataclass
class UserDC:
    id: int
    login: str
    nickname: str
    password: str

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @staticmethod
    def from_session(session: Session | None) -> UserforRequest | None:
        if session and session["user"]:
            return UserforRequest(
                id=session["user"]["id"],
                login=session["user"]["login"],
                nickname=session["user"]["nickname"],
            )
        return None
