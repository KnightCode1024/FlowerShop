from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.models import Base


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )
