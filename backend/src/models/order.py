import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from schemas.order import CartItem, OrderResponse, OrderStatus


class OrderProduct(Base):
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), primary_key=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, primary_key=False
    )
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="order_products",
    )
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)

    def __str__(self) -> str:
        return (
            f"OrderItem(order={self.order_id}, "
            f"product={self.product_id}, qty={self.quantity})"
        )


class Order(Base):
    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.IN_CART
    )
    amount: Mapped[float] = mapped_column(Float(), default=0.00)
    
    # Delivery address fields
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=True)
    recipient_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    delivery_address: Mapped[str] = mapped_column(Text(), nullable=True)
    delivery_city: Mapped[str] = mapped_column(String(100), nullable=True)
    delivery_zip: Mapped[str] = mapped_column(String(20), nullable=True)
    delivery_notes: Mapped[str] = mapped_column(Text(), nullable=True)

    def __str__(self) -> str:
        return f"Order #{self.id} ({self.status})"

    def to_entity(self) -> OrderResponse:
        return OrderResponse(
            id=self.id,
            order_products=[
                CartItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in (self.order_products or [])
            ],
            amount=self.amount,
            status=self.status,
            recipient_name=self.recipient_name,
            recipient_phone=self.recipient_phone,
            delivery_address=self.delivery_address,
            delivery_city=self.delivery_city,
            delivery_zip=self.delivery_zip,
            delivery_notes=self.delivery_notes,
        )
