from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    created = "created"
    processing = "processing"
    payed = "payed"


class Methods(str, Enum):
    YOOMONEY = "yoomoney"


class InvoiceCreateRequest(BaseModel):
    order_id: int
    user_id: int
    amount: int


class InvoiceCreate(BaseModel):
    uid: str
    name: str
    order_id: int
    user_id: int
    amount: int
    status: InvoiceStatus
    method: Methods


class InvoiceUpdateRequest(BaseModel):
    uid: str
    order_id: int
    user_id: int
    amount: int
    method: Methods


class InvoiceUpdate(BaseModel):
    name: str
    order_id: int
    user_id: int
    amount: int
    status: InvoiceStatus
    method: Methods
