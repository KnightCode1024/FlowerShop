from sqlalchemy import ForeignKey, Numeric, String, Enum

from models import Base
from sqlalchemy.orm import *

from schemas.invoice import InvoiceStatus


class Invoice(Base):
    name: Mapped[str] = mapped_column(String(length=64))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="user_order")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.created)
