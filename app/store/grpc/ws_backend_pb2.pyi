from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class GetUpdatesRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetUpdatesResponse(_message.Message):
    __slots__ = ["res"]

    class DocUpdates(_message.Message):
        __slots__ = ["document_id", "update"]
        DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
        UPDATE_FIELD_NUMBER: _ClassVar[int]
        document_id: str
        update: _containers.RepeatedScalarFieldContainer[str]
        def __init__(
            self,
            document_id: _Optional[str] = ...,
            update: _Optional[_Iterable[str]] = ...,
        ) -> None: ...
    RES_FIELD_NUMBER: _ClassVar[int]
    res: _containers.RepeatedCompositeFieldContainer[
        GetUpdatesResponse.DocUpdates
    ]
    def __init__(
        self,
        res: _Optional[
            _Iterable[_Union[GetUpdatesResponse.DocUpdates, _Mapping]]
        ] = ...,
    ) -> None: ...

class HandleDeleteRequest(_message.Message):
    __slots__ = ["document_id"]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    def __init__(self, document_id: _Optional[str] = ...) -> None: ...

class HandleDeleteResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class RemoveAccessRequest(_message.Message):
    __slots__ = ["document_id", "user_id"]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    user_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., document_id: _Optional[str] = ...
    ) -> None: ...

class RemoveAccessResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class SendTimestampRequest(_message.Message):
    __slots__ = ["document_id", "timestamp"]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    timestamp: str
    def __init__(
        self, document_id: _Optional[str] = ..., timestamp: _Optional[str] = ...
    ) -> None: ...

class SendTimestampResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...
