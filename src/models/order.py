from fifi import DatetimeDecoratedBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .portfolio import Portfolio
from ..enums.order_status import OrderStatus


class Order(DatetimeDecoratedBase):
    __tablename__ = "order"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolio.id"), nullable=False
    )
    market: Mapped[str] = mapped_column(nullable=False)
    commission: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stop_loss: Mapped[float]
    quantity: Mapped[float] = mapped_column(nullable=False)
    leverage: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.ACTIVE, nullable=False
    )

    # relationships
    portfolio: Mapped[Portfolio] = relationship("portfolio", back_populates="order")
