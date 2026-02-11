import datetime
import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from models import *


class OrderStatus(enum.StrEnum):
    IN_CART = "in_cart"
    WAITING_PAY = "waiting_pay"
    PAYED = "payed"
    ERROR = "error"


class OrderProduct(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, primary_key=False)
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="order_products"
    )
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)


class Order(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.IN_CART)
    amount: Mapped[float] = mapped_column(Float(), default=0.00)
