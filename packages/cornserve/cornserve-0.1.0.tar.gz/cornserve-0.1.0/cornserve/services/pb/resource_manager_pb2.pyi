import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeployUnitTaskRequest(_message.Message):
    __slots__ = ("task_instance_name",)
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    def __init__(self, task_instance_name: _Optional[str] = ...) -> None: ...

class DeployUnitTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class TeardownUnitTaskRequest(_message.Message):
    __slots__ = ("task_instance_name",)
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    def __init__(self, task_instance_name: _Optional[str] = ...) -> None: ...

class TeardownUnitTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class TaskManagerStatus(_message.Message):
    __slots__ = ("task_instance_name", "status")
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    status: _common_pb2.Status
    def __init__(self, task_instance_name: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class HealthcheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthcheckResponse(_message.Message):
    __slots__ = ("status", "task_manager_statuses")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TASK_MANAGER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    task_manager_statuses: _containers.RepeatedCompositeFieldContainer[TaskManagerStatus]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., task_manager_statuses: _Optional[_Iterable[_Union[TaskManagerStatus, _Mapping]]] = ...) -> None: ...

class ScaleUnitTaskRequest(_message.Message):
    __slots__ = ("task_instance_name", "num_gpus")
    TASK_INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    NUM_GPUS_FIELD_NUMBER: _ClassVar[int]
    task_instance_name: str
    num_gpus: int
    def __init__(self, task_instance_name: _Optional[str] = ..., num_gpus: _Optional[int] = ...) -> None: ...

class ScaleUnitTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...
