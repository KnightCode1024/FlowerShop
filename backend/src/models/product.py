from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models.category import Category
    from models.product_image import ProductImage


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

    images: Mapped[list[ProductImage]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ProductImage.order",
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    category: Mapped[Category] = relationship(
        "Category",
        back_populates="products",
    )
