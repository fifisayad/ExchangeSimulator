import pytest

from src.repository import PortfolioRepository
from src.repository import BalanceRepository
from src.repository import OrderRepository
from tests.materials import *


@pytest.mark.asyncio
class TestPortfolioRepository:
    portfilio_repo = PortfolioRepository()
    order_repo = OrderRepository()
    balance_repo = BalanceRepository()

    async def test_get_by_name(self, database_provider_test, portfolio_factory):
        portfolios_schema = [portfolio_factory() for i in range(5)]
        portfolios = await self.portfilio_repo.create_many(data=portfolios_schema)

        third_portfolio = await self.portfilio_repo.get_by_name(name=portfolios[3].name)
        assert third_portfolio is not None
        assert third_portfolio.id == portfolios[3].id

    async def test_remove_by_name(self, database_provider_test, portfolio_factory):
        portfolios_schema = [portfolio_factory() for i in range(5)]
        portfolios = await self.portfilio_repo.create_many(data=portfolios_schema)

        count = await self.portfilio_repo.remove_by_name(name=portfolios[3].name)

        assert count == 1

        third_portfolio = await self.portfilio_repo.get_one_by_id(id_=portfolios[3].id)

        assert third_portfolio is None
