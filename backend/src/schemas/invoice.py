from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    created = "created"
    processing = "processing"
    payed = "payed"


class Methods(str, Enum):
    YOOMONEY = "yoomoney"


class InvoiceCreateRequest(BaseModel):
    method: Methods
    order_id: int
    amount: int


class InvoiceCreate(BaseModel):
    uid: str
    name: str
    order_id: int
    user_id: int
    amount: float
    status: InvoiceStatus
    method: Methods


class InvoiceResponse(BaseModel):
    uid: str
    name: str
    order_id: int
    user_id: int
    link: str
    amount: float
    status: InvoiceStatus
    method: Methods
    link: str | None = None


class InvoiceUpdate(BaseModel):
    uid: str
    link: str | None = None
    amount: float | None = None
    method: Methods | None = None
    status: InvoiceStatus | None = None
