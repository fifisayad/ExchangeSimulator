from typing import Optional
from ..enums.asset import Asset
from ..models import Order
from ..repository import BalanceRepository


class BalanceService:

    def __init__(self):
        self.balance_repo = BalanceRepository()

    async def update_balances(self, order: Order) -> None:
        pass

    async def get_portfolio_asset_leverage(
        self, portfolio_id: str, asset: Asset
    ) -> Optional[float]:
        asset_balance = await self.balance_repo.get_portfolio_asset(
            portfolio_id=portfolio_id, asset=asset
        )
        if asset_balance:
            return asset_balance.leverage

    async def burn_balance(
        self, portfolio_id: str, asset: Asset, burned_qty: float
    ) -> bool:
        asset_balance = await self.balance_repo.get_portfolio_asset(
            portfolio_id=portfolio_id, asset=asset
        )
        if asset_balance:
            asset_balance.frozen -= burned_qty
            asset_balance.quantity -= burned_qty
            asset_balance.burned = burned_qty
            if asset_balance.quantity > 0 and asset_balance.frozen >= 0:
                await self.balance_repo.update_entity(asset_balance)
                return True
            else:
                raise ValueError(
                    f"{self.__class__.__name__}: burning asset is not possible... asset model is {asset_balance.to_dict()}"
                )
        return False
