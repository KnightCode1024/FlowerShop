from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from models import Base


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
