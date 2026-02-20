from datetime import datetime

from sqlalchemy import Integer, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__.lower()

        if name.endswith("y") and not name.endswith(
            ("ay", "ey", "iy", "oy", "uy"),
        ):
            return name[:-1] + "ies"
        elif name.endswith("s"):
            return name + "es"
        elif name.endswith(("sh", "ch", "x", "z")):
            return name + "es"
        else:
            return name + "s"
