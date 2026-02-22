from sqlalchemy import String, Integer, Numeric, ForeignKey

from models import Base
from sqlalchemy.orm import Mapped, mapped_column

from utils.strings import generate_random_promo


class Promocode(Base):
    code: Mapped[str] = mapped_column(
        String(),
        default=generate_random_promo,
    )
    count_activation: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
    )
    max_count_activators: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
    )
    percent: Mapped[float] = mapped_column(Numeric(10, 2))


class PromocodeActions(Base):
    promo_id: Mapped[int] = mapped_column(
        ForeignKey("promocodes.id"),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
