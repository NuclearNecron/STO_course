import asyncio
import json
from asyncio import Task, TaskGroup

import grpc
from grpc.aio import Server

import app.grpcio.ws_backend_pb2_grpc as ws_backend_pb2_grpc

import typing

from app.grpcio.ws_backend_pb2 import RemoveAccessResponse, HandleDeleteResponse

if typing.TYPE_CHECKING:
    from app.core.application import Application


class WS_Backend_ServiceServicer(ws_backend_pb2_grpc.WS_Backend_ServiceServicer):
    def __init__(self, app: "Application"):
        self.app = app

    async def SendTimestamp(self, request, context):
        # TODO: отфильтровать записи в Redis
        return

    async def RemoveAccess(self, request, context):
        """Закрытие всех соединений пользователя с данным документом"""
        await self.app.store.ws.disconnect_user(
            connection_key=(request.user_id, request.document_id),
            data=json.dumps({
                "type": "ACCESS_REMOVED",
                "payload": "У вас забрали доступ к документу!"
            })
        )
        return RemoveAccessResponse(status="ok")

    async def GetUpdates(self, request, context):
        # TODO: вернуть все обновления для всех доков
        return

    async def HandleDelete(self, request, context):
        await self.app.store.ws.disconnect_all_users_from_document(
            document_id=request.document_id,
            data=json.dumps({
                "type": "DOCUMENT_DELETED",
                "payload": "УВЫ!",
            })
        )
        await self.app.store.redis.delete_document(request.document_id)
        return HandleDeleteResponse(status="ok")


class gRPCServer:
    def __init__(self, app: "Application", listen_addr: str = "[::]:50051"):
        self.app = app
        self.server: Server = grpc.aio.server()
        self.service: WS_Backend_ServiceServicer = WS_Backend_ServiceServicer(app)
        self.listen_addr = listen_addr
        self.is_running: bool = False
        self.grpc_server_task: Task | None = None

    async def gracefully_start(self):
        await self.server.start()
        await self.server.wait_for_termination()

    async def serve(self, *_: list, **__: dict):
        ws_backend_pb2_grpc.add_WS_Backend_ServiceServicer_to_server(self.service, self.server)
        self.server.add_insecure_port(self.listen_addr)
        self.app.logger.info(f"gRPC сервер слушает сокет: {self.listen_addr}")
        self.is_running = True
        self.grpc_server_task = asyncio.create_task(self.gracefully_start())

    async def finish(self, *_: list, **__: dict):
        # Исправить финиш
        self.is_running = False
        if self.grpc_server_task:
            self.grpc_server_task.cancel()
            self.grpc_server_task = None
