from typing import List
from fifi import DatetimeDecoratedBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .balance import Balance
from .order import Order


class Portfolio(DatetimeDecoratedBase):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    orders: Mapped[List[Order]] = relationship(back_populates="portfolio")
    balances: Mapped[List[Balance]] = relationship(back_populates="portfolio")
