import uuid

from sqlalchemy import ForeignKey, Numeric, String, Enum, Uuid, Text

from models import Base
from sqlalchemy.orm import Mapped, mapped_column

from schemas.invoice import InvoiceStatus, Methods, InvoiceResponse


class Invoice(Base):
    uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=False, default=uuid.uuid4
    )
    method: Mapped[Methods] = mapped_column(
        Enum(
            Methods,
            name="methods",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )
    link: Mapped[str] = mapped_column(Text(), nullable=True)
    provider_uid: Mapped[str] = mapped_column(
        String(length=128),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(length=64))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.created
    )

    def to_entity(self):
        return InvoiceResponse(
            uid=self.uid,
            name=self.name,
            order_id=self.order_id,
            user_id=self.user_id,
            link=self.link,
            provider_uid=self.provider_uid,
            amount=self.amount,
            status=self.status,
            method=self.method,
            updated_at=self.updated_at,
        )
