from decimal import Decimal
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, ForeignKey

from models import Base


class Product(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    in_stock: Mapped[bool] = mapped_column(
        Boolean(),
        default=True,
    )

    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ProductImage.order",
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categorys.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )
