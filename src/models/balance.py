from fifi import DatetimeDecoratedBase
from fifi.enums import Asset

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Balance(DatetimeDecoratedBase):
    __tablename__ = "balances"
    # columns
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )
    asset: Mapped[Asset] = mapped_column(nullable=False)
    quantity: Mapped[float] = mapped_column(
        CheckConstraint("quantity >= 0", name="ck_quantity_positive"), nullable=False
    )
    available: Mapped[float] = mapped_column(
        CheckConstraint("available >= 0", name="ck_available_positive"), nullable=False
    )
    frozen: Mapped[float] = mapped_column(
        CheckConstraint("frozen >= 0", name="ck_frozen_positive"), nullable=False
    )
    burned: Mapped[float] = mapped_column(
        CheckConstraint("burned >= 0", name="ck_burned_positive"),
        default=0,
        nullable=False,
    )
    fee_paid: Mapped[float] = mapped_column(
        CheckConstraint("fee_paid >= 0", name="ck_fee_paid_positive"),
        default=0,
        nullable=False,
    )

    # constraints
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id", "asset", name="balance_uq_portfolio_asset_combination"
        ),
    )
    # relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="balances"
    )
