from fifi import DatetimeDecoratedBase
from fifi.enums import Market
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Leverage(DatetimeDecoratedBase):
    __tablename__ = "leverages"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    market: Mapped[Market] = mapped_column(nullable=False)
    leverage: Mapped[float] = mapped_column(default=0, nullable=False)

    # constraints
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id", "market", name="levearage_uq_portfolio_market_combination"
        ),
    )
    # relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="leverages"
    )
