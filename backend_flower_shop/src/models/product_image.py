from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean

from models import Base


class ProductImage(Base):
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer(),
        default=0,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="images",
    )
