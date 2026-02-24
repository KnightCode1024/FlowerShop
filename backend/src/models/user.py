import uuid
from enum import StrEnum

from sqlalchemy import UUID, Boolean
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
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    token: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        default=uuid.uuid4(),
        nullable=True,
    )
    otp_secret: Mapped[str] = mapped_column(
        String(),
        nullable=True,
    )
