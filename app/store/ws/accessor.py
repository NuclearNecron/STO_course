import asyncio
import typing
from asyncio import Queue, TaskGroup
from collections import defaultdict

import marshmallow.exceptions
from aiohttp import WSMessage
from aiohttp.web import WebSocketResponse

from app.base.base_accessor import BaseAccessor
from app.core.application import Request
from app.store.ws.dataclasses import WSConnection, Event
from app.store.ws.schemes import EventSchema

if typing.TYPE_CHECKING:
    from app.core.application import Application


USER_DOC_KEY = tuple[str, str]  # тип для ключа WebSocket соединения


class WSAccessor(BaseAccessor):
    _heartbeat: float | None = (
        None  # Каждые heartbeat секунд пингуем соединение
    )
    _connections: dict[
        USER_DOC_KEY, list[WSConnection]
    ] | None = None  # Словарь пользователей и их WebSocket соединений

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self._connections = defaultdict(list)
        self._heartbeat = 20.0

    async def handle_request(self, request: "Request"):
        """Обработка запроса на обновление соединения до WebSocket"""
        ws_response = WebSocketResponse(heartbeat=self._heartbeat)
        await ws_response.prepare(request)
        request.user_credentials = "USER_ID: 1"
        connection_key = (str(request.user_credentials), "DOC_ID: 1")
        self._connections[connection_key].append(
            WSConnection(ws_connection=ws_response, msg_queue=Queue())
        )
        await self.read(
            connection_key, len(self._connections[connection_key]) - 1
        )
        await self.close(
            connection_key, len(self._connections[connection_key]) - 1
        )
        return ws_response

    async def read(self, connection_key: USER_DOC_KEY, ws_pipe_index: int):
        """Чтение сообщения из WebSocket соединения"""
        message: WSMessage
        async for message in self._connections[connection_key][
            ws_pipe_index
        ].ws_connection:
            try:
                event: Event = EventSchema().loads(message.data)
                await self.push_selected(
                    selected_connections=[connection_key], data=message.data
                )
            except marshmallow.exceptions.ValidationError:
                # TODO: отправить сообщение на фронт, что тип сообщения не выдержан
                await self.push_selected(
                    selected_connections=[connection_key],
                    data=str("Увы, неверный формат сообщения был отправлен"),
                )
                return

    async def close(self, connection_key: USER_DOC_KEY, ws_pipe_index: int):
        """Закрытие WebSocket соединения"""
        try:
            connection = self._connections[connection_key].pop(ws_pipe_index)
            if len(self._connections[connection_key]) == 0:
                self._connections.pop(connection_key)
            await connection.ws_connection.close()
        except KeyError:
            return

    async def push_selected(
        self, selected_connections: list[USER_DOC_KEY], data: str
    ):
        """Отправка сообщения по WebSocket соединениям с выбранными ключами"""
        tg: TaskGroup
        async with asyncio.TaskGroup() as tg:
            for connection_key in self._connections.keys():
                if connection_key in selected_connections:
                    tg.create_task(self._push(connection_key, data))
        return

    async def push_selected_doc(self, _doc: str, data: str):
        """Отправка сообщения все пользователям, редактирующим данный документ"""
        tg: TaskGroup
        async with asyncio.TaskGroup() as tg:
            for user, doc in self._connections.keys():
                if doc == _doc:
                    tg.create_task(self._push((user, doc), data))
        return

    async def _push(self, connection_key: USER_DOC_KEY, data: str):
        """Отправка сообщения по WebSocket соединению по ключу пользователь-документ"""
        try:
            tg: TaskGroup
            async with asyncio.TaskGroup() as tg:
                for ws in self._connections[connection_key]:
                    tg.create_task(ws.ws_connection.send_str(data))
        except KeyError:
            return
        except ConnectionResetError:
            self._connections.pop(connection_key)
            return
