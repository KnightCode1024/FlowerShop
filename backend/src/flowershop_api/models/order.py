import datetime
import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.flowershop_api.models import Base
from src.flowershop_api.models import *


class OrderStatus(enum.StrEnum):
    IN_CART = "in_cart"
    WAITING_PAY = "waiting_pay"
    PAYED = "payed"
    ERROR = "error"


class OrderProduct(Base):
    id = None
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="order_products"
    )
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)


class Order(Base):
    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="orders")

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.IN_CART)
    amount: Mapped[float] = mapped_column(Float(), default=0.00)
