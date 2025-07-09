from typing import List
from fifi import DatetimeDecoratedBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .balance import Balance
from .order import Order


class Portfolio(DatetimeDecoratedBase):
    __tablename__ = "portfolio"
    # columns
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    # relationships
    orders: Mapped[List[Order]] = relationship("order", back_populates="portfolio")
    balances: Mapped[List[Balance]] = relationship(
        "balance", back_populates="portfolio"
    )
