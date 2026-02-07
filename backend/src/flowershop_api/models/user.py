from enum import Enum, StrEnum

from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.flowershop_api.models import Base
from src.flowershop_api.models.order import *


class RoleEnum(StrEnum):
    USER = "user"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum),
        default=RoleEnum.USER,
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )
