import asyncio
import json
import typing
import uuid
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
        USER_DOC_KEY, dict[str, WSConnection]
    ] | None = None  # Словарь пользователей и их WebSocket соединений

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self._connections = defaultdict(dict)
        self._heartbeat = 20.0

    async def handle_request(self, request: "Request"):
        """Обработка запроса на обновление соединения до WebSocket"""
        # TODO: авторизация?
        user, doc = request.user_credentials, request.match_info["document_id"]
        ws_response = WebSocketResponse(heartbeat=self._heartbeat)
        await ws_response.prepare(request)
        ws_pipe_key = str(uuid.uuid4())
        self._connections[(user, doc)][ws_pipe_key] = WSConnection(
            ws_connection=ws_response, msg_queue=Queue()
        )
        updates = await self.app.store.redis.get_all_updates(doc)
        for update in updates:
            await self.push_selected([(user, doc)], update)
        await self.read((user, doc), ws_pipe_key)
        await self.close((user, doc), ws_pipe_key)
        return ws_response

    async def read(self, connection_key: USER_DOC_KEY, ws_pipe_key: str):
        """Чтение сообщений из WebSocket соединения"""
        user, doc = connection_key
        message: WSMessage
        async for message in self._connections[connection_key][
            ws_pipe_key
        ].ws_connection:
            try:
                event: Event = EventSchema().loads(message.data)
                await self.app.store.redis.append_update(doc, EventSchema().dumps(event))
                await self.push_selected_doc(doc, EventSchema().dumps(event))
            except marshmallow.exceptions.ValidationError as e:
                await self.push_selected(
                    selected_connections=[connection_key],
                    data=f"Неверный формат сообщения: {str(e.data)}",
                )
                return

    async def close(self, connection_key: USER_DOC_KEY, ws_pipe_key: str):
        """Закрытие WebSocket соединения"""
        try:
            connection = self._connections[connection_key].pop(ws_pipe_key)
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
            for connection_key in selected_connections:
                tg.create_task(self._push(connection_key, data))
        return

    async def push_selected_doc(self, document: str, data: str):
        """Отправка сообщения все пользователям, редактирующим данный документ"""
        tg: TaskGroup
        async with asyncio.TaskGroup() as tg:
            for user, doc in self._connections.keys():
                if doc == document:
                    tg.create_task(self._push((user, doc), data))
        return

    async def _push(self, connection_key: USER_DOC_KEY, data: str):
        """Отправка сообщения по всем WebSocket соединениям с данным ключом пользователь-документ"""
        try:
            tg: TaskGroup
            async with asyncio.TaskGroup() as tg:
                ws: WSConnection
                for ws in self._connections[connection_key].values():
                    tg.create_task(ws.ws_connection.send_str(data))
        except KeyError:
            return
        # except ConnectionResetError:
        #     self._connections.pop(connection_key)
        #     return
