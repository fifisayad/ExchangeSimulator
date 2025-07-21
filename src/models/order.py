from fifi import DatetimeDecoratedBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums.market import Market
from ..enums.order_side import OrderSide
from ..enums.order_type import OrderType
from ..enums.order_status import OrderStatus


class Order(DatetimeDecoratedBase):
    __tablename__ = "orders"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    market: Mapped[Market] = mapped_column(nullable=False)
    fee: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    size: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.ACTIVE, nullable=False
    )
    type: Mapped[OrderType] = mapped_column(default=OrderType.LIMIT, nullable=False)
    side: Mapped[OrderSide] = mapped_column(nullable=False)
    positon_id: Mapped[str] = mapped_column(nullable=True)

    # relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="orders")
