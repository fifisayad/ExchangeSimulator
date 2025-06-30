from fifi import DatetimeDecoratedBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .portfolio import Portfolio
from ..enums.order_status import OrderStatus


class Order(DatetimeDecoratedBase):
    market: Mapped[str] = mapped_column(nullable=False)
    commission: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stop_loss: Mapped[float]
    quantity: Mapped[float] = mapped_column(nullable=False)
    leverage: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.ACTIVE, nullable=False
    )
    portfolio: Mapped[Portfolio] = relationship(back_populates="orders")
