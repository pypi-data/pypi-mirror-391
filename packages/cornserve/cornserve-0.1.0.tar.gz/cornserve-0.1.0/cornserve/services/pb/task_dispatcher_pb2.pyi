import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskManagerDeployment(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class NotifyUnitTaskDeploymentRequest(_message.Message):
    __slots__ = ("task_instance_name", "task_manager")
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_MANAGER_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    task_manager: TaskManagerDeployment
    def __init__(self, task_instance_name: _Optional[str] = ..., task_manager: _Optional[_Union[TaskManagerDeployment, _Mapping]] = ...) -> None: ...

class NotifyUnitTaskDeploymentResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class NotifyUnitTaskTeardownRequest(_message.Message):
    __slots__ = ("task_instance_name",)
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    def __init__(self, task_instance_name: _Optional[str] = ...) -> None: ...

class NotifyUnitTaskTeardownResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...
