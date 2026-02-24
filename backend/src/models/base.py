import uuid
from datetime import datetime

import inflect
from sqlalchemy import Integer, func
from sqlalchemy import Integer, func, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)

p = inflect.engine()


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )
    # uid: Mapped[Uuid] = mapped_column(
    #     Uuid(as_uuid=True),
    #     primary_key=False,
    #     default=uuid.uuid4
    # )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__
        snake_case = "".join(
            ["_" + c.lower() if c.isupper() else c for c in name]
        ).lstrip("_")
        plural = p.plural(snake_case)
        return plural

    def __repr__(self):
        cols = []
        for num, col in enumerate(self.__table__.columns.keys()):
            cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {','.join(cols)}>"

