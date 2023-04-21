from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentDC:
    id: int
    name: str
    path: str
    owner_id: int
    last_edited: datetime


@dataclass
class UserDocDC:
    id: int
    user_id: int
    doc_id: int
    access: str
