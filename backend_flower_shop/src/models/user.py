from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum as SQLEnum

from models import Base


class RoleEnum(str, Enum):
    USER = "user"
    EMPLOYEE = "employee"
    ADMIN = "admin"
    ANONYMOUS = "anonymous"


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
