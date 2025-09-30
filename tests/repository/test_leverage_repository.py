import pytest

from fifi.exceptions import IntegrityConflictException
from fifi.enums import Market

from src.repository import LeverageRepository
from tests.materials import *


@pytest.mark.asyncio
class TestLeverageRepository:
    leverage_repository = LeverageRepository()

    async def test_get_all_leverages(self, database_provider_test, leverage_factory):
        leverage_schemas = leverage_factory()
        leverages = await self.leverage_repository.create_many(data=leverage_schemas)

        assert len(leverage_schemas) == len(leverages)

        got_leverages = await self.leverage_repository.get_all_leverages()

        assert len(got_leverages) == len(leverages)

        leverage_ids = set()
        for leverage in leverages:
            leverage_ids.add(leverage.id)

        for leverage in got_leverages:
            assert leverage.id in leverage_ids

    async def test_leverage_unique_constraint(
        self, database_provider_test, leverage_factory
    ):
        leverage_schemas = leverage_factory(count=1)
        for leverage in leverage_schemas:
            leverage.market = Market.BTCUSD_PERP

        with pytest.raises(IntegrityConflictException):
            await self.leverage_repository.create_many(data=leverage_schemas)

    async def test_get_by_portfolio_market(
        self, database_provider_test, leverage_factory
    ):
        leverage_schemas = leverage_factory()
        leverages = await self.leverage_repository.create_many(data=leverage_schemas)

        for leverage in leverages:
            got_leverage = (
                await self.leverage_repository.get_leverage_by_portfolio_id_and_market(
                    portfolio_id=leverage.portfolio_id, market=leverage.market
                )
            )
            assert got_leverage is not None
            assert got_leverage.id == leverage.id
            assert got_leverage.leverage == leverage.leverage
