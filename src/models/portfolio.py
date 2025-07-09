from typing import List
from fifi import DatetimeDecoratedBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Portfolio(DatetimeDecoratedBase):
    __tablename__ = "portfolios"
    # columns
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    # relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="portfolio")
    balances: Mapped[List["Balance"]] = relationship(
        "Balance", back_populates="portfolio"
    )
