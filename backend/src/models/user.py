from enum import StrEnum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class RoleEnum(StrEnum):
    USER = "user"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class User(Base):
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
        SQLEnum(
            RoleEnum,
            name="roleenum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=RoleEnum.USER,
        nullable=False,
    )
