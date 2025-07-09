from fifi import DatetimeDecoratedBase
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums.asset import Asset
from .portfolio import Portfolio


class Balance(DatetimeDecoratedBase):
    __tablename__ = "balance"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolio.id"), nullable=False
    )
    asset: Mapped[Asset] = mapped_column(nullable=False)
    quantity: Mapped[float] = mapped_column(
        CheckConstraint("value >= 0", name="ck_value_positive"), nullable=False
    )
    available: Mapped[float] = mapped_column(
        CheckConstraint("value >= 0", name="ck_value_positive"), nullable=False
    )
    frozen: Mapped[float] = mapped_column(
        CheckConstraint("value >= 0", name="ck_value_positive"), nullable=False
    )
    # relationships
    portfolio: Mapped[Portfolio] = relationship("portfolio", back_populates="balances")
