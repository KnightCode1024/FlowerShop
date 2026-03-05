import uuid

from sqlalchemy import Enum, ForeignKey, Numeric, String

from models import Base
from sqlalchemy.orm import Mapped, mapped_column

from schemas.invoice import InvoiceStatus, Methods


class Invoice(Base):
    uid: Mapped[str] = mapped_column(
        String(length=36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    method: Mapped[Methods] = mapped_column(Enum(Methods), nullable=False)
    link: Mapped[str] = mapped_column(String(length=256), nullable=True)
    name: Mapped[str] = mapped_column(String(length=64))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.created)

    def __str__(self) -> str:
        return f"Invoice #{self.id} ({self.status})"
