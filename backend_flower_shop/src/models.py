from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class Post(Base):
    title: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
