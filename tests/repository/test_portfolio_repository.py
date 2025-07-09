from fifi import DecoratedBase
import pytest

from src import PortfolioRepository
from src.repository.balance_repository import BalanceRepository
from src.repository.order_repository import OrderRepository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestPortfolioRepository:
    portfilio_repo = PortfolioRepository()
    order_repo = OrderRepository()
    balance_repo = BalanceRepository()

    async def test_get_by_name(self, database_provider_test, portfolio_factory):
        LOGGER.info(database_provider_test)
        LOGGER.info(f"decorated base meta data: {DecoratedBase.metadata.tables}")
        portfolios_schema = [portfolio_factory() for i in range(5)]
        portfolios = await self.portfilio_repo.create_many(
            data=portfolios_schema, return_models=True
        )

        third_portfolio = await self.portfilio_repo.get_by_name(name=portfolios[3].name)

        assert third_portfolio.id == portfolios[3].id
