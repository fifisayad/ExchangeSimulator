import pytest

from src.models import Leverage
from src.services import LeverageService
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestLeverageService:
    leverage_service = LeverageService()

    async def test_get_portfolio_market_leverage(
        self, database_provider_test, leverage_factory
    ):
        leverages_schemas = leverage_factory()
        leverages = await self.leverage_service.create_many(leverages_schemas)

        for leverage in leverages:
            got_leverage = await self.leverage_service.get_portfolio_market_leverage(
                portfolio_id=leverage.portfolio_id, market=leverage.market
            )

            assert got_leverage is not None
            assert got_leverage.leverage == leverage.leverage
