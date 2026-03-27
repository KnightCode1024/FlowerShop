from enum import Enum
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    created = "created"
    processing = "processing"
    payed = "payed"


class Methods(str, Enum):
    YOOMONEY = "yoomoney"
    STRIPE = "stripe"


class InvoiceCreateRequest(BaseModel):
    method: Methods
    order_id: int
    amount: float


class InvoiceCreate(BaseModel):
    name: str
    order_id: int
    user_id: int
    amount: float
    status: InvoiceStatus
    method: Methods


class InvoiceResponse(BaseModel):
    uid: UUID
    name: str
    order_id: int
    user_id: int
    amount: float
    status: InvoiceStatus
    method: Methods
    link: str | None = None
    provider_uid: str | None = None
    updated_at: datetime | None = None


class InvoiceUpdate(BaseModel):
    uid: UUID
    link: str | None = None
    provider_uid: str | None = None
    amount: float | None = None
    method: Methods | None = None
    status: InvoiceStatus | None = None
