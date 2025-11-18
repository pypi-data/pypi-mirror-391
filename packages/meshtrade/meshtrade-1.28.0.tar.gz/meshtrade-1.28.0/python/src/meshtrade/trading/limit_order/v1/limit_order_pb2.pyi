from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LimitOrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIMIT_ORDER_SIDE_UNSPECIFIED: _ClassVar[LimitOrderSide]
    LIMIT_ORDER_SIDE_BUY: _ClassVar[LimitOrderSide]
    LIMIT_ORDER_SIDE_SELL: _ClassVar[LimitOrderSide]

class LimitOrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIMIT_ORDER_STATUS_UNSPECIFIED: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_SUBMISSION_IN_PROGRESS: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_SUBMISSION_FAILED: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_OPEN: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_COMPLETE_IN_PROGRESS: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_COMPLETE: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_CANCELLATION_IN_PROGRESS: _ClassVar[LimitOrderStatus]
    LIMIT_ORDER_STATUS_CANCELLED: _ClassVar[LimitOrderStatus]
LIMIT_ORDER_SIDE_UNSPECIFIED: LimitOrderSide
LIMIT_ORDER_SIDE_BUY: LimitOrderSide
LIMIT_ORDER_SIDE_SELL: LimitOrderSide
LIMIT_ORDER_STATUS_UNSPECIFIED: LimitOrderStatus
LIMIT_ORDER_STATUS_SUBMISSION_IN_PROGRESS: LimitOrderStatus
LIMIT_ORDER_STATUS_SUBMISSION_FAILED: LimitOrderStatus
LIMIT_ORDER_STATUS_OPEN: LimitOrderStatus
LIMIT_ORDER_STATUS_COMPLETE_IN_PROGRESS: LimitOrderStatus
LIMIT_ORDER_STATUS_COMPLETE: LimitOrderStatus
LIMIT_ORDER_STATUS_CANCELLATION_IN_PROGRESS: LimitOrderStatus
LIMIT_ORDER_STATUS_CANCELLED: LimitOrderStatus

class LimitOrder(_message.Message):
    __slots__ = ("name", "owner", "account", "external_reference", "side", "limit_price", "quantity", "fill_price", "filled_quantity", "status")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FILL_PRICE_FIELD_NUMBER: _ClassVar[int]
    FILLED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    account: str
    external_reference: str
    side: LimitOrderSide
    limit_price: _amount_pb2.Amount
    quantity: _amount_pb2.Amount
    fill_price: _amount_pb2.Amount
    filled_quantity: _amount_pb2.Amount
    status: LimitOrderStatus
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., account: _Optional[str] = ..., external_reference: _Optional[str] = ..., side: _Optional[_Union[LimitOrderSide, str]] = ..., limit_price: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., quantity: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., fill_price: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., filled_quantity: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., status: _Optional[_Union[LimitOrderStatus, str]] = ...) -> None: ...
