from typing import Optional
from src.enums.asset import Asset
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
        return await self.balance_repo.get_portfolio_asset_leverage(
            portfolio_id=portfolio_id, asset=asset
        )
