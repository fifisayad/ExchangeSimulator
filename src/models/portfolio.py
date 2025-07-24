from typing import List
from fifi import DatetimeDecoratedBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.settings import Setting


class Portfolio(DatetimeDecoratedBase):
    __tablename__ = "portfolios"
    # columns
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    spot_maker_fee: Mapped[float] = mapped_column(
        default=Setting().DEFAULT_SPOT_MAKER_FEE, nullable=False
    )
    spot_taker_fee: Mapped[float] = mapped_column(
        default=Setting().DEFAULT_SPOT_TAKER_FEE, nullable=False
    )
    perp_maker_fee: Mapped[float] = mapped_column(
        default=Setting().DEFAULT_PERP_MAKER_FEE, nullable=False
    )
    perp_taker_fee: Mapped[float] = mapped_column(
        default=Setting().DEFAULT_PERP_TAKER_FEE, nullable=False
    )
    # relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="portfolio")  # type: ignore
    balances: Mapped[List["Balance"]] = relationship(  # type: ignore
        "Balance", back_populates="portfolio"
    )
    positions: Mapped[List["Position"]] = relationship(  # type: ignore
        "Position", back_populates="portfolio"
    )
    leverages: Mapped[List["Leverage"]] = relationship(  # type: ignore
        "Leverage", back_populates="portfolio"
    )
