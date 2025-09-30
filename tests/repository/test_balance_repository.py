import pytest

from fifi.enums import Asset

from src.repository import PortfolioRepository
from src.repository import BalanceRepository
from src.repository import OrderRepository

from tests.materials import *


@pytest.mark.asyncio
class TestBalanceRepository:
    portfilio_repo = PortfolioRepository()
    order_repo = OrderRepository()
    balance_repo = BalanceRepository()

    async def test_get_all_balances(
        self, database_provider_test, portfolio_factory, balance_factory_for_portfolios
    ):
        portfolios_schema = [portfolio_factory() for i in range(5)]
        portfolios = await self.portfilio_repo.create_many(data=portfolios_schema)

        for portfolio in portfolios:  # type: ignore
            balances_schema = balance_factory_for_portfolios(portfolio.id)
            balances_created = await self.balance_repo.create_many(data=balances_schema)
            assert len(balances_schema) == len(balances_created)

        balances = await self.balance_repo.get_all_balances()

        assert len(balances) == Asset.__len__() * 5

    async def test_get_portfolio_asset(
        self, database_provider_test, portfolio_factory, balance_factory_for_portfolios
    ) -> None:
        portfolio_schema = portfolio_factory()
        portfolio = await self.portfilio_repo.create(data=portfolio_schema)

        balances_schema = balance_factory_for_portfolios(portfolio.id)
        balances = await self.balance_repo.create_many(data=balances_schema)

        for balance in balances:
            got_balance = await self.balance_repo.get_portfolio_asset(
                portfolio_id=balance.portfolio_id, asset=balance.asset
            )
            assert got_balance is not None
            assert got_balance.to_dict() == balance.to_dict()
