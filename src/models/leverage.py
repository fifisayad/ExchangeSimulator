from fifi import DatetimeDecoratedBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums.market import Market


class Leverage(DatetimeDecoratedBase):
    __tablename__ = "leverages"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    market: Mapped[Market] = mapped_column(nullable=False)
    leverage: Mapped[float] = mapped_column(default=0, nullable=False)

    # relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="leverages"
    )
