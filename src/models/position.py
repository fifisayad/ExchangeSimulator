from fifi import DatetimeDecoratedBase
from fifi.enums import PositionSide, PositionStatus, Market

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Position(DatetimeDecoratedBase):
    __tablename__ = "positions"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    market: Mapped[Market] = mapped_column(nullable=False)
    leverage: Mapped[float] = mapped_column(nullable=False)
    entry_price: Mapped[float] = mapped_column(nullable=False)
    close_price: Mapped[float] = mapped_column(default=0, nullable=False)
    lqd_price: Mapped[float] = mapped_column(nullable=False)
    pnl: Mapped[float] = mapped_column(default=0, nullable=False)
    size: Mapped[float] = mapped_column(nullable=False)
    margin: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[PositionStatus] = mapped_column(
        default=PositionStatus.OPEN, nullable=False
    )
    side: Mapped[PositionSide] = mapped_column(nullable=False)

    # relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="positions"
    )
