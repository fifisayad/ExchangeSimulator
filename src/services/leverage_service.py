from typing import Optional
from fifi import GetLogger


from .service import Service
from ..enums.market import Market
from ..models import Leverage
from ..repository import LeverageRepository

LOGGER = GetLogger().get()


class LeverageService(Service):
    def __init__(self):
        self._repo = LeverageRepository()

    @property
    def repo(self) -> LeverageRepository:
        return self._repo

    async def get_portfolio_market_leverage(
        self, portfolio_id: str, market: Market
    ) -> Optional[float]:
        leverage = await self.repo.get_leverage_by_portfolio_id_and_market(
            portfolio_id=portfolio_id, market=market
        )
        if leverage:
            return leverage.leverage

    async def update_leverage(
        self, portfolio_id: str, market: Market, leverage: float
    ) -> Optional[Leverage]:
        leverage_model = await self.repo.get_leverage_by_portfolio_id_and_market(
            portfolio_id=portfolio_id, market=market
        )
        if leverage_model:
            leverage_model.leverage = leverage
            LOGGER.info(f"updating {portfolio_id=} {market=} {leverage=}")
            await self.update_entity(leverage_model)
        return leverage_model
