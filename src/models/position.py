from fifi import DatetimeDecoratedBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums.position_side import PositionSide
from ..enums.position_status import PositionStatus
from ..enums.market import Market


class Position(DatetimeDecoratedBase):
    __tablename__ = "positions"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    market: Mapped[Market] = mapped_column(nullable=False)
    leverage: Mapped[float] = mapped_column(nullable=False)
    entry_price: Mapped[float] = mapped_column(nullable=False)
    lqd_price: Mapped[float] = mapped_column(nullable=False)
    pnl: Mapped[float] = mapped_column(nullable=False)
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
