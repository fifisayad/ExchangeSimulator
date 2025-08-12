from typing import List, Optional
import logging

from fifi import GetLogger, BaseService

from src.models.balance import Balance
from src.schemas.balance_schema import BalanceSchema

from ..enums.asset import Asset
from ..models import Order
from ..repository import BalanceRepository


LOGGER = logging.getLogger(__name__)


class BalanceService(BaseService):
    """Service responsible for managing portfolio asset balances,
    including leverage retrieval, balance unlocking, burning, and updates
    related to trading activity."""

    def __init__(self):
        """Initializes the BalanceService with its associated repository."""
        self._repo = BalanceRepository()

    @property
    def repo(self) -> BalanceRepository:
        return self._repo

    async def burn_balance(
        self, portfolio_id: str, asset: Asset, burned_qty: float
    ) -> bool:
        """Burns (reduces) balance and frozen funds from a portfolio asset, simulating a loss.

        Args:
            portfolio_id (str): The ID of the portfolio.
            asset (Asset): The asset to deduct balance from.
            burned_qty (float): The amount to burn.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        asset_balance = await self.read_by_asset(portfolio_id=portfolio_id, asset=asset)
        if asset_balance:
            asset_balance.frozen -= burned_qty
            asset_balance.quantity -= burned_qty
            asset_balance.burned += burned_qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False

    async def unlock_balance(
        self, portfolio_id: str, asset: Asset, unlocked_qty: float
    ) -> bool:
        """Unlocks frozen balance and makes it available for use.

        Args:
            portfolio_id (str): The ID of the portfolio.
            asset (Asset): The asset to modify.
            unlocked_qty (float): The amount to unlock.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        asset_balance = await self.read_by_asset(portfolio_id, asset)
        if asset_balance:
            asset_balance.frozen -= unlocked_qty
            asset_balance.available += unlocked_qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False

    async def lock_balance(
        self, portfolio_id: str, asset: Asset, locked_qty: float
    ) -> bool:
        """Lock available balance and freeze it.

        Args:
            portfolio_id (str): The ID of the portfolio.
            asset (Asset): The asset to modify.
            locked_qty (float): The amount to lock.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        asset_balance = await self.read_by_asset(portfolio_id, asset)
        if asset_balance:
            asset_balance.frozen += locked_qty
            asset_balance.available -= locked_qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False

    async def add_balance(self, portfolio_id: str, asset: Asset, qty: float) -> bool:
        """Adds balance to a portfolio asset, typically as realized PnL.

        Args:
            portfolio_id (str): The ID of the portfolio.
            asset (Asset): The asset to add to.
            qty (float): The amount to add.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        asset_balance = await self.read_by_asset(portfolio_id, asset)
        if asset_balance:
            asset_balance.quantity += qty
            asset_balance.available += qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False

    async def read_many_by_portfolio_id(self, portfolio_id: str) -> List[Balance]:
        return await self.repo.get_entities_by_portfolio_id(portfolio_id=portfolio_id)

    async def read_by_asset(self, portfolio_id: str, asset: Asset) -> Optional[Balance]:
        return await self.repo.get_portfolio_asset(
            portfolio_id=portfolio_id, asset=asset
        )

    async def create_by_qty(
        self, portfolio_id: str, asset: Asset, qty: float
    ) -> Balance:
        balance_schema = BalanceSchema(
            portfolio_id=portfolio_id,
            asset=asset,
            quantity=qty,
            available=qty,
            frozen=0,
        )

        LOGGER.info(
            f"creating new balance for {portfolio_id=}, {asset.value=} with {qty=}"
        )
        return await self.create(data=balance_schema)

    async def check_available_qty(
        self, portfolio_id: str, asset: Asset, qty: float
    ) -> bool:
        balance = await self.read_by_asset(portfolio_id=portfolio_id, asset=asset)
        if balance:
            if balance.available >= qty:
                return True
        return False

    async def pay_balance(
        self, portfolio_id: str, asset: Asset, paid_qty: float
    ) -> bool:
        asset_balance = await self.read_by_asset(portfolio_id, asset)
        if asset_balance:
            asset_balance.available -= paid_qty
            asset_balance.quantity -= paid_qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False

    async def pay_fee(self, portfolio_id: str, asset: Asset, paid_qty: float) -> bool:
        asset_balance = await self.read_by_asset(portfolio_id, asset)
        if asset_balance:
            asset_balance.fee_paid += paid_qty
            asset_balance.available -= paid_qty
            asset_balance.quantity -= paid_qty
            await self.repo.update_entity(asset_balance)
            return True
        LOGGER.warning(f"No balance found for {portfolio_id=} {asset=}")
        return False
