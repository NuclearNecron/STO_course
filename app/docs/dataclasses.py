from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentDC:
    id: int
    name: str
    owner_id: int
    last_edited: datetime


@dataclass
class UserDocDC:
    id: int
    user_id: int
    doc_id: int
    access: str


@dataclass
class UserforDoc:
    id: int
    nickname: str


@dataclass
class fullDoc:
    id: int
    name: str
    owner: UserforDoc
    last_edited: datetime


@dataclass
class fullAccess:
    id: int
    user: UserforDoc
    doc_id: int
    access: str
