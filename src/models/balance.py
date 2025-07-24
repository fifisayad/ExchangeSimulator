from fifi import DatetimeDecoratedBase
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums.asset import Asset


class Balance(DatetimeDecoratedBase):
    __tablename__ = "balances"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    asset: Mapped[Asset] = mapped_column(nullable=False)
    quantity: Mapped[float] = mapped_column(
        CheckConstraint("quantity >= 0", name="ck_value_positive"), nullable=False
    )
    available: Mapped[float] = mapped_column(
        CheckConstraint("available >= 0", name="ck_value_positive"), nullable=False
    )
    frozen: Mapped[float] = mapped_column(
        CheckConstraint("frozen >= 0", name="ck_value_positive"), nullable=False
    )
    burned: Mapped[float] = mapped_column(
        CheckConstraint("frozen >= 0", name="ck_value_positive"),
        default=0,
        nullable=False,
    )

    # relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="balances"
    )
