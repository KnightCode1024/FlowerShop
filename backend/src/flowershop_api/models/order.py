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
    __tablename__ = "order_products"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    order: Mapped["Order"] = relationship(
        back_populates="order_products"
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)


class Order(Base):
    __tablename__ = "orders"

    order_products: Mapped[list["OrderProduct"]] = mapped_column(
        "OrderProduct",
        back_populates="order",
        use_list=True,
        lazy="joinedload",
        cascade="all, delete-orphan"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="orders", nullable=False)

    status: Mapped[OrderStatus] = mapped_column(Enum(), default=OrderStatus.IN_CART)
    amount: Mapped[float] = mapped_column(Float(), default=0.00)
