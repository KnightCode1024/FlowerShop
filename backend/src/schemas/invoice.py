from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(Enum):
    created = "created"
    processing = "processing"
    payed = "payed"


class InvoiceCreateRequest(BaseModel):
    order_id: int
    user_id: int
    amount: int


class InvoiceCreate(BaseModel):
    name: str
    order_id: int
    user_id: int
    amount: int
    status: InvoiceStatus



class InvoiceUpdateRequest(BaseModel):
    uid: str
    order_id: int
    user_id: int
    amount: int


class InvoiceUpdate(BaseModel):
    name: str
    order_id: int
    user_id: int
    amount: int
    status: InvoiceStatus
