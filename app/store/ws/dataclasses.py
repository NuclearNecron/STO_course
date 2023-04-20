from asyncio import Queue
from dataclasses import dataclass

from aiohttp.web_ws import WebSocketResponse


@dataclass
class WSConnection:
    ws_connection: WebSocketResponse
    msg_queue: Queue


@dataclass
class Event:
    type: str
    payload: dict
