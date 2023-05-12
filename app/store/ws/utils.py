from asyncio import Queue
from dataclasses import dataclass

from aiohttp.web_ws import WebSocketResponse
from marshmallow import Schema, fields, post_load

from app.core.utils import BetterEnum


@dataclass
class WSConnection:
    ws_connection: WebSocketResponse
    msg_queue: Queue


class WSMessageType(BetterEnum):
    CONNECTED = "CONNECTED"
    UPDATE = "UPDATE"
    DISCONNECTED = "DISCONNECTED"
    SERVICE = "SERVICE"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"


class WSServiceMessage(BetterEnum):
    DOCUMENT_DELETED = "Документ был удален. К сожалению, вы не можете более его редактировать"
    NO_RIGHTS_TO_WRITE = (
        "К сожалению, у вас забрали права на редактирование документа"
    )
    SUCCESSFULLY_CONNECTED = "Подключение успешно! Теперь вы можете совместно редактировать этот документ"
    DISCONNECTED = ""


@dataclass
class WSMessage:
    type: str
    payload: dict


class EventSchema(Schema):
    type = fields.Str(required=True)
    payload = fields.Dict(required=True)

    @post_load
    def make_Event(self, data, **kwargs) -> WSMessage:
        return WSMessage(**data)
