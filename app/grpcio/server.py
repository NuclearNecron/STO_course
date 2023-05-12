import asyncio
import json
import typing
from asyncio import Task

import grpc
from grpc.aio import Server

import app.grpcio.ws_backend_pb2_grpc as ws_backend_pb2_grpc
from app.grpcio.ws_backend_pb2 import (
    RemoveAccessResponse,
    HandleDeleteResponse,
    SendTimestampResponse,
    GetUpdatesResponse,
)

if typing.TYPE_CHECKING:
    from app.core.application import Application


class WS_Backend_ServiceServicer(
    ws_backend_pb2_grpc.WS_Backend_ServiceServicer
):
    def __init__(self, app: "Application"):
        self.app = app

    async def SendTimestamp(self, request, context):
        self.app.logger.info(
            f"gRPC: запрос на удаление изменений в документе {request.document_id} с временной меткой ранее {request.timestamp}"
        )
        await self.app.store.redis.filter_updates(
            document=request.document_id,
            timestamp=request.timestamp,
        )
        return SendTimestampResponse(status="ok")

    async def RemoveAccess(self, request, context):
        """Закрытие всех соединений пользователя с данным документом"""
        self.app.logger.info(
            f"gRPC: запрос на отзыв доступа клиенту {request.user_id} к документу {request.document_id}"
        )
        await self.app.store.ws.disconnect_user(
            connection_key=(request.user_id, request.document_id),
            data=json.dumps(
                {
                    "type": "ACCESS_REMOVED",
                    "payload": "У вас забрали доступ к документу!",
                }
            ),
        )
        return RemoveAccessResponse(status="ok")

    async def GetUpdates(self, request, context):
        self.app.logger.info(
            "gRPC: запрос на получение изменений в документах"
        )
        raw_result = await self.app.store.redis.get_all_documents_updates()
        extent = []
        for k, v in raw_result:
            tmp = GetUpdatesResponse.DocUpdates(document_id=k)
            tmp.update.extend(v)
            extent.append(tmp)
        response = GetUpdatesResponse()
        response.res.extend(extent)
        return response

    async def HandleDelete(self, request, context):
        """Обработка удаления документа"""
        self.app.logger.info(
            f"gRPC: запрос на удаление документа: {request.document_id}"
        )
        await self.app.store.ws.disconnect_all_users_from_document(
            document_id=request.document_id,
            data=json.dumps(
                {
                    "type": "DOCUMENT_DELETED",
                    "payload": "УВЫ!",
                }
            ),
        )
        await self.app.store.redis.delete_document(request.document_id)
        return HandleDeleteResponse(status="ok")


class gRPCServer:
    def __init__(
        self, app: "Application", listen_addr: str = "localhost:50051"
    ):
        self.app = app
        self.server: Server = grpc.aio.server()
        self.service: WS_Backend_ServiceServicer = WS_Backend_ServiceServicer(
            app
        )
        self.listen_addr: str = listen_addr
        self.is_running: bool = False
        self.grpc_server_task: Task | None = None

    async def _grpc_server_start(self):
        self.is_running = True
        self.app.logger.info(
            f"Запуск gRPC сервера слушающего адрес: {self.listen_addr} ..."
        )
        await self.server.start()
        self.app.logger.info(f"gRPC сервер запущен")
        await self.server.wait_for_termination()
        await self.server.stop(5.0)

    async def serve(self, *_: list, **__: dict):
        ws_backend_pb2_grpc.add_WS_Backend_ServiceServicer_to_server(
            self.service, self.server
        )
        self.server.add_insecure_port(self.listen_addr)
        self.grpc_server_task = asyncio.create_task(self._grpc_server_start())

    async def finish(self, *_: list, **__: dict):
        # TODO: graceful finish
        self.is_running = False
        if self.grpc_server_task:
            await self.grpc_server_task
            self.grpc_server_task = None
